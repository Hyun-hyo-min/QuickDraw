from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db_session
from app.auth.jwt import get_current_user_id
from app.auth.validator import validate_user_id
from app.db.models import Room, Player
from app.db.repositories import RoomRepository, PlayerRepository
from app.schemas.requests import CreateRoomRequest
from app.schemas.responses import RoomInfoResponse, PlayerInfoResponse

router = APIRouter()


@router.post("/")
async def create_room(
    body: CreateRoomRequest,
    user_id: UUID = Depends(get_current_user_id),
    player_repository: PlayerRepository = Depends(PlayerRepository),
    room_repository: RoomRepository = Depends(RoomRepository)
):
    await validate_user_id(user_id)

    existing_player = await player_repository.find_one_by_filter({"user_id": user_id})
    if existing_player:
        raise HTTPException(
            status_code=400,
            detail="User already in a room."
        )

    room_id = uuid4()
    room = Room(id=room_id, name=body.room_name, user_id=user_id)
    player = Player(user_id=user_id, room_id=room_id)

    try:
        await room_repository.insert_data(room)
        await player_repository.insert_data(player)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create room: {str(e)}"
        )

    return {"message": "Room created", "room_id": room.id}


@router.post("/{room_id}/players")
async def join_room(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    player_repository: PlayerRepository = Depends(PlayerRepository),
    room_repository: RoomRepository = Depends(RoomRepository)
):
    room = await room_repository.find_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    players = await player_repository.find_all_by_filter({"room_id": room_id})
    if len(players) >= room.max_players:
        raise HTTPException(status_code=400, detail="Room is full.")

    if any(player.user_id == user_id for player in players):
        return {"message": f"{user_id} already joined the room"}

    existing_player = await player_repository.find_one_by_filter({"user_id": user_id})
    if existing_player:
        raise HTTPException(
            status_code=400, detail="User already in another room.")

    await player_repository.insert_data(Player(user_id=user_id, room_id=room_id))

    return {"message": f"{user_id} joined the room"}


@router.delete("/{room_id}/players")
async def quit_room(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    player_repository: PlayerRepository = Depends(PlayerRepository)
):
    player = await player_repository.find_one_by_filter({"user_id": user_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found.")

    if room_id != player.room_id:
        raise HTTPException(
            status_code=400, detail="Player is not in the" f"{room_id} room.")

    await player_repository.delete_data(player)

    return {"message": f"{user_id} quited the room"}


@router.get("/{room_id}", response_model=RoomInfoResponse)
async def room_info(
    room_id: UUID,
    player_repository: PlayerRepository = Depends(PlayerRepository),
    room_repository: RoomRepository = Depends(RoomRepository)
):
    room = await room_repository.find_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    players = await player_repository.find_all_by_filter({"room_id": room_id})
    players_info = []
    for player in players:
        players_info.append(
            PlayerInfoResponse.model_validate(player, from_attributes=True)
        )

    room_info = RoomInfoResponse.model_validate(room, from_attributes=True)
    room_info.players = players_info

    return room_info


@router.get("/current")
async def get_current_room(
    user_id: UUID = Depends(get_current_user_id),
    player_repository: PlayerRepository = Depends(PlayerRepository),
):
    await validate_user_id(user_id)
    player = await player_repository.find_one_by_filter({"user_id": user_id})

    if not player:
        raise HTTPException(
            status_code=404,
            detail="user not in room"
        )

    room_id = player.room_id
    return {"room_id": room_id}


@router.get("/")
async def get_rooms(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    offset = (page - 1) * page_size
    room_query = (
        select(Room, func.count(Player.id).label("player_count"))
        .outerjoin(Player, Room.id == Player.room_id)
        .group_by(Room.id)
        .order_by(Room.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    room_result = await session.execute(room_query)
    rooms = room_result.fetchall()

    room_infos = []
    for room, player_count in rooms:
        room_infos.append(RoomInfoResponse(
            id=room.id,
            user_id=room.user_id,
            name=room.name,
            status=room.status,
            player_count=player_count,
        ))

    total_count_query = select(func.count(Room.id))
    total_count_result = await session.execute(total_count_query)
    total_count = total_count_result.scalar()

    total_pages = (total_count + page_size - 1) // page_size

    return {"rooms": room_infos, "total_pages": total_pages}


@router.delete("/{room_id}")
async def delete_room(
    room_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    room_repository: RoomRepository = Depends(RoomRepository)
):
    room = await room_repository.find_by_id(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    if room.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this room.")

    await room_repository.delete_data(room)

    return {"message": f"room {room_id} deleted"}
