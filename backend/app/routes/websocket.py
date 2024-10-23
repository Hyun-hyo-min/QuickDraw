import asyncio
import json
from redis import asyncio as aioredis
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from fastapi.websockets import WebSocketDisconnect
from service.redis import get_redis_pool
from service.managers import ws_manager, MaximumSessionReachException, MaximumConnectionPerSessionReachException
from service.sessions import update_session_expiration, add_player_to_session

router = APIRouter()

@router.websocket("/rooms/{room_id}")
async def room_websocket_endpoint(
    websocket: WebSocket, 
    room_id: int, 
    redis: Annotated[aioredis.Redis, Depends(get_redis_pool)]
):
    try:
        session_data = await redis.get(room_id)
        if not session_data:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=404, detail="Session not found")
        session_data = json.loads(session_data)

        if len(session_data["players"]) >= 8:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=403, detail="Session is full")

        await websocket.accept()

        try:
            ws_manager.add_client(room_id, websocket)
        except MaximumSessionReachException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=403, detail="Maximum number of sessions exceeded")
        except MaximumConnectionPerSessionReachException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=403, detail="Maximum number of connections per session exceeded")

        await add_player_to_session(session_data, websocket.client)
        await update_session_expiration(session_data)
        await redis.set(
            room_id, 
            json.dumps(session_data), 
            ex=(datetime.fromisoformat(session_data["expires_at"]) - datetime.now()).seconds
        )

        pubsub = redis.pubsub()
        await pubsub.subscribe(room_id)

        async def receive_messages():
            try:
                while True:
                    received_data = await websocket.receive_text()
                    await redis.publish(room_id, received_data)
            except WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"Error while receiving messages: {e}")

        async def send_messages():
            try:
                async for message in pubsub.listen():
                    if message['type'] == 'message':
                        data = message['data']
                        await websocket.send_text(data.decode('utf-8'))
            except Exception as e:
                print(f"메시지 전송 중 오류 발생: {e}")

        receive_task = asyncio.create_task(receive_messages())
        send_task = asyncio.create_task(send_messages())

        await asyncio.gather(receive_task, send_task)

    except Exception as e:
        print(f"WebSocket 엔드포인트 오류 발생: {e}")
    finally:
        # 정리 작업
        await pubsub.unsubscribe(room_id)
        await pubsub.close()
        ws_manager.remove_client(room_id, websocket)
        await websocket.close()
