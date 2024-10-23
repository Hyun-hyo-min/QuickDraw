import asyncio
import json
import logging
from redis import asyncio as aioredis
from fastapi import WebSocket, HTTPException, status
from fastapi.websockets import WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketSession:
    def __init__(self, id: int, email: str, websocket: WebSocket, redis: aioredis.Redis):
        self.id = str(id)
        self.email = email
        self.websocket = websocket
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        self.is_closed = False

    async def validate_session(self):
        session_data = await self.redis.get(self.id)

        if not session_data:
            await self.close_websocket(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=404, detail="Session not found.")

        session_data = json.loads(session_data)

        if len(session_data.get("clients", [])) >= 8:
            await self.close_websocket(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(
                status_code=403, detail="Maximum connections per session exceeded.")

        return session_data

    async def accept_connection(self):
        await self.websocket.accept()

    async def subscribe_channel(self):
        await self.pubsub.subscribe(self.id)

    async def unsubscribe_channel(self):
        await self.pubsub.unsubscribe(self.id)
        await self.pubsub.close()

    async def receive_messages(self):
        try:
            while True:
                received_data = await self.websocket.receive_text()
                await self.redis.publish(self.id, received_data)
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {self.websocket.client}")
            await self.handle_disconnection()
        except Exception as e:
            logger.error(f"Error while receiving message: {e}")
            await self.close_websocket(code=status.WS_1011_INTERNAL_ERROR)

    async def send_messages(self):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    await self.websocket.send_text(data.decode("utf-8"))
        except Exception as e:
            logger.error(f"Error while sending message: {e}")
            await self.close_websocket(code=status.WS_1011_INTERNAL_ERROR)

    async def run(self):
        receive_task = asyncio.create_task(self.receive_messages())
        send_task = asyncio.create_task(self.send_messages())
        await asyncio.gather(receive_task, send_task)

    async def close_websocket(self, code):
        if not self.is_closed:
            await self.websocket.close(code=code)
            self.is_closed = True

    async def handle_disconnection(self):
        session_key = f"session:{self.id}:clients"
        await self.redis.srem(session_key, self.email)
        logger.info(f"Removed client {self.email} from set {session_key}")
