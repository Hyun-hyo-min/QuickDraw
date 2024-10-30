from fastapi import APIRouter, HTTPException, WebSocket, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from service.redis_managers import ClientSessionInterface, DrawSessionInterface, get_client_manager, get_draw_manager
from service.db_managers import DBManagerInterface, get_db_manager
from service.websocket_sessions import RoomWebSocketSession

router = APIRouter()


@router.websocket("/rooms/{session_id}/{email}")
async def room_websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    email: str,
    client_manager: ClientSessionInterface = Depends(get_client_manager),
    draw_manager: DrawSessionInterface = Depends(get_draw_manager),
    db_manager: DBManagerInterface = Depends(get_db_manager),
    db_session: AsyncSession = Depends(get_db_session)
):
    session = RoomWebSocketSession(
        session_id,
        email,
        websocket,
        client_manager,
        draw_manager,
        db_manager,
        db_session
    )

    try:
        await session.run()
    except Exception as e:
        await session.close_websocket(code=status.WS_1011_INTERNAL_ERROR)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Websocket endpoint error: {e}"
        )
    finally:
        await session.handle_disconnection()
