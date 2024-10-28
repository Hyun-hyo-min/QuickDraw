from typing import List
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from models.bases import UserBase, RoomBase, PlayerBase
from models.enums import RoomStatus


class User(UserBase, table=True):
    email: EmailStr = Field(primary_key=True, index=True)
    password: str = Field(nullable=True)


class Room(RoomBase, table=True):
    id: int = Field(primary_key=True)
    host: EmailStr = Field(foreign_key='user.email')
    name: str
    status: RoomStatus = Field(default=RoomStatus.WAITING)
    players: List["Player"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Player(PlayerBase, table=True):
    id: int = Field(primary_key=True)
    email: EmailStr = Field(foreign_key='user.email')
    room_id: int = Field(foreign_key="room.id")
    room: Room = Relationship(back_populates="players")
