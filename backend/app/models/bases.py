from sqlmodel import SQLModel
from pydantic import EmailStr
from models.enums import RoomStatus


class UserBase(SQLModel):
    name: str
    email: EmailStr
    password: str


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


class DrawingBase(SQLModel):
    id: int
    room_id: int
    x: float
    y: float
    prev_x: float
    prev_y: float