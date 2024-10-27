from fastapi import APIRouter, HTTPException, WebSocket, Depends, status
from typing import Annotated
from redis import asyncio as aioredis
from service.redis import get_redis_pool
from service.sessions import WebSocketSession

router = APIRouter()


@router.websocket("/rooms/{room_id}/{email}")
async def room_websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    email: str,
    redis: Annotated[aioredis.Redis, Depends(get_redis_pool)]
):
    session = WebSocketSession(room_id, email, websocket, redis)

    try:
        await session.run()
    except Exception as e:
        await session.close_websocket(code=status.WS_1011_INTERNAL_ERROR)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Websocket endpoint error: {e}")
    finally:
        await session.handle_disconnection()
