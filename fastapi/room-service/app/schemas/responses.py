from uuid import UUID
from pydantic import BaseModel
from app.schemas.enums import RoomStatus


class PlayerInfoResponse(BaseModel):
    id: UUID
    user_id: UUID


class RoomInfoResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    status: RoomStatus
    max_players: int = 8
    player_count: int = 0
    players: list[PlayerInfoResponse] = []