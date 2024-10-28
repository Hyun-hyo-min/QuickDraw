import asyncio
import logging
import json
from redis import asyncio as aioredis
from fastapi import WebSocket, HTTPException, status
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from service.redis import RedisSessionManager
from models.models import Drawing

logger = logging.getLogger(__name__)


class WebSocketSession:
    def __init__(self, id, email: str, websocket: WebSocket, redis: aioredis.Redis, db_session: AsyncSession):
        self.id = id
        self.email = email
        self.websocket = websocket
        self.session_manager = RedisSessionManager(id, redis)
        self.db_session = db_session
        self.is_closed = False

    async def validate_session(self):
        if not await self.session_manager.session_exists():
            await self.session_manager.add_client(self.email)
            return

        client_count = await self.session_manager.get_client_count()
        if client_count >= 8:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Maximum connections per session exceeded.")

    async def accept_connection(self):
        await self.websocket.accept()
        await self.session_manager.add_client(self.email)

    async def close_websocket(self, code=status.WS_1000_NORMAL_CLOSURE):
        if not self.is_closed:
            await self.websocket.close(code=code)
            self.is_closed = True

    async def handle_receive_messages(self):
        try:
            while True:
                received_data = await self.websocket.receive_text()
                data = json.loads(received_data)

                if data.get("type") == "draw":
                    await self.session_manager.save_draw_data(data)

                await self.session_manager.publish_client(received_data)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {self.websocket.client}")
            await self.handle_disconnection()

        except Exception as e:
            logger.error(f"Error while receiving message: {e}")
            await self.close_websocket(code=status.WS_1011_INTERNAL_ERROR)

    async def handle_send_messages(self):
        try:
            async for message in self.session_manager.listen():

                if message["type"] == "message" and not self.is_closed:
                    data = message["data"]
                    await self.websocket.send_text(data.decode("utf-8"))

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {self.websocket.client}")
            await self.handle_disconnection()

        except Exception as e:
            logger.error(f"Error while sending message: {e}")
            await self.close_websocket(code=status.WS_1011_INTERNAL_ERROR)

    async def handle_disconnection(self):
        await self.session_manager.remove_client(self.email)
        client_count = await self.session_manager.get_client_count()
        if client_count == 0:
            await self.session_manager.delete_client_session()
        self.is_closed = True
        logger.info(f"Client {self.email} disconnected from session {self.id}")

    async def save_draw_data_to_db(self):
        while not self.is_closed:
            await asyncio.sleep(5)
            drawings = await self.session_manager.get_all_draw_data()
            if drawings:
                insert_values = [
                    {
                        "room_id": self.id,
                        "x": drawing_data["x"],
                        "y": drawing_data["y"],
                        "prev_x": drawing_data["prevX"],
                        "prev_y": drawing_data["prevY"]
                    }
                    for drawing_data in drawings
                ]

                await self.db_session.execute(
                    Drawing.__table__.insert(),
                    insert_values
                )
                await self.db_session.commit()
                await self.session_manager.clear_draw_data()

    async def run(self):
        await self.validate_session()
        await self.accept_connection()

        receive_task = asyncio.create_task(self.handle_receive_messages())
        send_task = asyncio.create_task(self.handle_send_messages())
        save_task = asyncio.create_task(self.save_draw_data_to_db())

        await asyncio.gather(receive_task, send_task, save_task)