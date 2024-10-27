import asyncio
import json
import logging
from redis import asyncio as aioredis
from fastapi import WebSocket, HTTPException, status
from fastapi.websockets import WebSocketDisconnect
from service.redis import RedisSessionManager

logger = logging.getLogger(__name__)


class WebSocketSession:
    def __init__(self, id: int, email: str, websocket: WebSocket, redis: aioredis.Redis):
        self.id = str(id)
        self.email = email
        self.websocket = websocket
        self.session_manager = RedisSessionManager(id, redis)
        self.is_closed = False

    async def validate_session(self):
        if not await self.session_manager.session_exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

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
                await self.session_manager.publish(received_data)
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
            await self.session_manager.delete_session()
        self.is_closed = True
        logger.info(f"Client {self.email} disconnected from session {self.id}")

    async def run(self):
        await self.validate_session()
        await self.accept_connection()
        receive_task = asyncio.create_task(self.handle_receive_messages())
        send_task = asyncio.create_task(self.handle_send_messages())
        await asyncio.gather(receive_task, send_task)
