from fastapi import APIRouter, Query, WebSocket, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.connection import get_db_session
from auth.jwt import get_current_user
from models.rooms import Room, Player
from schemas.rooms import RoomCreateRequest
from typing import List

room_router = APIRouter(
    tags=["Room"],
)


@room_router.post("/")
async def create_room(
    body: RoomCreateRequest,
    email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(select(Player).where(Player.email == email))
    existing_player = result.scalars().first()

    if existing_player:
        raise HTTPException(
            status_code=400, detail="User already in the room.")

    new_room = Room(name=body.room_name, host=email)
    new_player = Player(email=email, room=new_room)
    session.add_all([new_room, new_player])

    await session.commit()
    await session.refresh(new_room)

    return {"message": "Room created", "room_id": new_room.id}


@room_router.post("/join/{room_id}")
async def join_room(
    room_id: int,
    email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(
        select(Room)
        .options(selectinload(Room.players))
        .where(Room.id == room_id)
    )
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    if len(room.players) >= room.max_players:
        raise HTTPException(status_code=400, detail="Room is full.")

    result = await session.execute(select(Player).where(Player.email == email))
    existing_player = result.scalars().first()
    if existing_player:
        raise HTTPException(
            status_code=400, detail="User already in the room.")

    new_player = Player(email=email, room_id=room_id)
    session.add(new_player)
    await session.commit()
    await session.refresh(new_player)

    return {"message": f"{email} joined the room"}


@room_router.get("/{room_id}")
async def room_info(room_id: int, session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(
        select(Room)
        .options(selectinload(Room.players))
        .where(Room.id == room_id)
    )
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    return {
        "room_name": room.name,
        "host": room.host,
        "players": [player.email for player in room.players],
        "status": room.status
    }


@room_router.get("/", response_model=List[Room])
async def get_rooms(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    offset = (page - 1) * page_size
    limit = page_size

    result = await session.execute(
        select(Room)
        .offset(offset)
        .limit(limit)
    )
    rooms = result.scalars().all()

    if not rooms:
        raise HTTPException(status_code=404, detail="No rooms found.")

    return rooms


@room_router.delete("/{room_id}")
async def delete_room(room_id: int, session: AsyncSession = Depends(get_db_session)):
    room = await session.get(Room, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    await session.delete(room)
    await session.commit()

    return {"message": f"room {room_id} deleted"}
