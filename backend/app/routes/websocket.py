# websocket.py
from fastapi import APIRouter, WebSocket, HTTPException, Depends, status
from service.websocket_sessions import RoomWebSocketSessionFactory

router = APIRouter()


@router.websocket("/rooms/{session_id}/{email}")
async def room_websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    email: str,
    session_factory: RoomWebSocketSessionFactory = Depends(
        RoomWebSocketSessionFactory)
):
    session = session_factory.create_session(session_id, email, websocket)

    try:
        await session.run()
    except Exception as e:
        await session.close_websocket(code=status.WS_1011_INTERNAL_ERROR)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebSocket endpoint error: {e}"
        )
    finally:
        await session.handle_disconnection()
