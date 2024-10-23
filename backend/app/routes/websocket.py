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
        # Redis에서 세션 데이터 가져오기
        session_data = await redis.get(room_id)
        if not session_data:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=404, detail="Session not found")
        session_data = json.loads(session_data)

        # 방에 인원이 가득 찼는지 확인
        if len(session_data["players"]) >= 8:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=403, detail="Session is full")

        # WebSocket 연결 수락
        await websocket.accept()

        # 클라이언트를 ws_manager에 추가
        try:
            ws_manager.add_client(room_id, websocket)
        except MaximumSessionReachException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=403, detail="Maximum number of sessions exceeded")
        except MaximumConnectionPerSessionReachException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=403, detail="Maximum number of connections per session exceeded")

        # 세션에 플레이어 추가 및 만료 시간 업데이트
        await add_player_to_session(session_data, websocket.client)
        await update_session_expiration(session_data)
        await redis.set(
            room_id, 
            json.dumps(session_data), 
            ex=(datetime.fromisoformat(session_data["expires_at"]) - datetime.now()).seconds
        )

        # Redis Pub/Sub 설정
        pubsub = redis.pubsub()
        await pubsub.subscribe(room_id)

        async def receive_messages():
            try:
                while True:
                    # 클라이언트로부터 메시지 수신
                    received_data = await websocket.receive_text()
                    # Redis 채널에 메시지 발행
                    await redis.publish(room_id, received_data)
            except WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"메시지 수신 중 오류 발생: {e}")

        async def send_messages():
            try:
                async for message in pubsub.listen():
                    if message['type'] == 'message':
                        data = message['data']
                        # 클라이언트에게 메시지 전송
                        await websocket.send_text(data.decode('utf-8'))
            except Exception as e:
                print(f"메시지 전송 중 오류 발생: {e}")

        # 수신 및 전송 태스크 동시 실행
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
