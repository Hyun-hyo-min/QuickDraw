import json
from typing import Annotated
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from redis import asyncio as aioredis
from database.connection import get_db_session
from auth.jwt import get_current_user
from models.models import Room, Player
from schemas.schemas import RoomCreateRequest, RoomResponse
from service.redis import get_redis_pool

router = APIRouter()


@router.post("/")
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

    room = Room(name=body.room_name, host=email)
    player = Player(email=email, room=room)
    session.add_all([room, player])

    await session.commit()
    await session.refresh(room)

    return {"message": "Room created", "room_id": room.id}


@router.post("/{room_id}/players")
async def join_room(room_id: int, email: str = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
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


@router.delete("/{room_id}/players")
async def quit_room(room_id: int, email: str = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(
        select(Player)
        .where(Player.email == email)
    )
    player = result.scalars().first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found.")

    if room_id != player.room_id:
        raise HTTPException(
            status_code=400, detail="Player is not in the" f"{room_id} room.")

    await session.delete(player)
    await session.commit()

    return {"message": f"{email} quited the room"}


@router.get("/{room_id}")
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


@router.get("/")
async def get_rooms(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    offset = (page - 1) * page_size
    limit = page_size

    total_rooms = await session.execute(select(Room))
    total_rooms_count = len(total_rooms.scalars().all())

    result = await session.execute(
        select(Room)
        .options(selectinload(Room.players))
        .offset(offset)
        .limit(limit)
        .order_by(Room.id.desc())
    )
    rooms = result.scalars().all()

    if not rooms:
        raise HTTPException(status_code=404, detail="No rooms found.")

    rooms = [
        RoomResponse(
            id=room.id,
            name=room.name,
            host=room.host,
            status=room.status,
            max_players=room.max_players,
            current_players=len(room.players)
        )
        for room in rooms
    ]

    total_pages = (total_rooms_count + page_size - 1) // page_size

    return {"rooms": rooms, "total_pages": total_pages}


@router.delete("/{room_id}")
async def delete_room(room_id: int, email: str = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)):
    room = await session.get(Room, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    if room.host != email:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this room.")

    await session.delete(room)
    await session.commit()

    return {"message": f"room {room_id} deleted"}


@router.post("/session/{room_id}")
async def create_room_session(
    room_id: int,
    redis: Annotated[aioredis.Redis, Depends(get_redis_pool)],
    email: str = Depends(get_current_user)
):
    session_id = str(room_id)
    session_key = f"session:{session_id}:clients"

    await redis.sadd(session_key, email)
    await redis.expire(session_key, 300)

    return {"url": f"/ws/rooms/{room_id}/{email}"}