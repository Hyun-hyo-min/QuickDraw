from fastapi import APIRouter, HTTPException, WebSocket, Depends, status
from typing import Annotated
from redis import asyncio as aioredis
from service.redis import get_redis_pool, RedisSessionManager
from service.sessions import WebSocketSession

router = APIRouter()


@router.websocket("/rooms/{room_id}/{email}")
async def room_websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    email: str,
    redis: Annotated[aioredis.Redis, Depends(get_redis_pool)]
):
    session_manager = RedisSessionManager(room_id, redis)
    session = WebSocketSession(room_id, email, websocket, redis)

    try:
        if not await session_manager.session_exists():
            await session.close_websocket(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=404, detail="Session not found")

        # 현재 접속자 수 확인
        client_count = await session_manager.get_client_count()
        if client_count >= 8:
            await session.close_websocket(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(
                status_code=403, detail="Maximum connections per session exceeded")

        await session.accept_connection()
        await session_manager.add_client_to_session(email)

        await session.subscribe_channel()
        await session.run()

    except Exception as e:
        await session.close_websocket(code=status.WS_1011_INTERNAL_ERROR)
        raise HTTPException(
            status_code=500, detail=f"Websocket endpoint error: {e}")

    finally:
        await session.unsubscribe_channel()
        await session_manager.remove_client(email)
        await session.close_websocket(code=status.WS_1000_NORMAL_CLOSURE)
