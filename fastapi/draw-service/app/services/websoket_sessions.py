import asyncio
import logging
import json
from uuid import UUID
from abc import ABC, abstractmethod
from fastapi import WebSocket, HTTPException, status, Depends
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.redis_managers import ClientSessionInterface, DrawSessionInterface, get_client_manager, get_draw_manager
from app.services.db_managers import DBManagerInterface, get_db_manager
from app.db.connection import get_db_session

logger = logging.getLogger(__name__)


class BaseWebSocketSession(ABC):
    def __init__(
        self,
        session_id: str,
        user_id: str,
        websocket: WebSocket,
        client_manager: ClientSessionInterface,
        draw_manager: DrawSessionInterface,
        db_manager: DBManagerInterface,
        db_session: AsyncSession
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.websocket = websocket
        self.client_manager = client_manager
        self.draw_manager = draw_manager
        self.db_manager = db_manager
        self.db_session = db_session
        self.is_closed = False

    async def validate_session(self):
        client_count = await self.client_manager.get_client_count()
        if client_count is None:
            await self.client_manager.add_client(self.user_id)
            return
        if client_count >= 8:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Maximum connections per session exceeded."
            )

    @abstractmethod
    async def accept_connection(self):
        pass

    async def close_websocket(self, code=status.WS_1000_NORMAL_CLOSURE):
        if not self.is_closed:
            await self.websocket.close(code=code)
            self.is_closed = True

    async def handle_disconnection(self):
        await self.client_manager.remove_client(self.user_id)
        client_count = await self.client_manager.get_client_count()
        if client_count == 0:
            await self.client_manager.delete_client_session()
        self.is_closed = True
        logger.info(f"Client {self.user_id} disconnected from session {
                    self.session_id}")

    @abstractmethod
    async def handle_receive_messages(self):
        pass

    @abstractmethod
    async def handle_send_messages(self):
        pass

    async def save_draw_data_to_db(self):
        while not self.is_closed:
            await asyncio.sleep(5)

            if not await self.draw_manager.session_exists():
                logger.info(
                    f"Room {self.session_id} has been deleted. Stopping draw data save.")
                break

            drawings = await self.draw_manager.get_all_draw_data()
            if drawings:
                try:
                    await self.db_manager.save_drawings(drawings, self.session_id, self.db_session)
                finally:
                    await self.draw_manager.clear_draw_data()

    async def run(self):
        await self.validate_session()
        await self.accept_connection()

        receive_task = asyncio.create_task(self.handle_receive_messages())
        send_task = asyncio.create_task(self.handle_send_messages())
        save_task = asyncio.create_task(self.save_draw_data_to_db())

        await asyncio.gather(receive_task, send_task, save_task)


class RoomWebSocketSession(BaseWebSocketSession):
    async def accept_connection(self):
        await self.websocket.accept()
        await self.client_manager.add_client(self.user_id)

    async def handle_receive_messages(self):
        try:
            while True:
                received_data = await self.websocket.receive_text()
                data = json.loads(received_data)

                if data.get("type") == "draw":
                    await self.draw_manager.save_draw_data(data)

                await self.client_manager.publish_client(received_data)

        except WebSocketDisconnect:
            logger.info(f"Room WebSocket disconnected: {
                        self.websocket.client}")
            await self.handle_disconnection()

    async def handle_send_messages(self):
        try:
            async for message in self.client_manager.listen():
                if message["type"] == "message" and not self.is_closed:
                    data = message["data"]
                    await self.websocket.send_text(data.decode("utf-8"))

        except WebSocketDisconnect:
            logger.info(f"Room WebSocket disconnected: {
                        self.websocket.client}")
            await self.handle_disconnection()


class RoomWebSocketSessionFactory:
    def __init__(
        self,
        client_manager: ClientSessionInterface = Depends(get_client_manager),
        draw_manager: DrawSessionInterface = Depends(get_draw_manager),
        db_manager: DBManagerInterface = Depends(get_db_manager),
        db_session: AsyncSession = Depends(get_db_session)
    ):
        self.client_manager = client_manager
        self.draw_manager = draw_manager
        self.db_manager = db_manager
        self.db_session = db_session

    def create_session(
        self, session_id: str, user_id: str, websocket: WebSocket
    ) -> RoomWebSocketSession:
        return RoomWebSocketSession(
            session_id,
            user_id,
            websocket,
            self.client_manager,
            self.draw_manager,
            self.db_manager,
            self.db_session
        )
