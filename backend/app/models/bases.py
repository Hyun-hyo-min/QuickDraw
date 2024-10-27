from sqlmodel import SQLModel
from pydantic import EmailStr
from models.enums import RoomStatus

class UserBase(SQLModel):
    name: str
    email: EmailStr

class RoomBase(SQLModel):
    id: int
    host: EmailStr
    name: str
    status: RoomStatus
    max_players: int = 8


class PlayerBase(SQLModel):
    id: int
    email: EmailStr
    room_id: int

