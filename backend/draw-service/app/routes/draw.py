from uuid import UUID
from fastapi import APIRouter, WebSocket, HTTPException, status, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.websoket_sessions import RoomWebSocketSessionFactory
from app.db.connection import get_db_session
from app.db.models import Drawing

router = APIRouter()


@router.get("/{room_id}")
async def get_drawings(
    room_id: UUID,
    session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(select(Drawing).where(Drawing.room_id == room_id))
    drawings = result.scalars()
    return [{"x": drawing.x, "y": drawing.y, "prevX": drawing.prev_x, "prevY": drawing.prev_y} for drawing in drawings]


@router.websocket("/{session_id}/user/{user_id}")
async def room_websocket_endpoint(
    websocket: WebSocket,
    session_id: UUID,
    user_id: UUID,
    session_factory: RoomWebSocketSessionFactory = Depends(
        RoomWebSocketSessionFactory)
):
    session = session_factory.create_session(session_id, user_id, websocket)

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
