from typing import List
from pydantic import EmailStr
from sqlmodel import Field, Relationship
from models.bases import UserBase, RoomBase, PlayerBase, DrawingBase
from models.enums import RoomStatus


class User(UserBase, table=True):
    email: EmailStr = Field(primary_key=True, index=True)
    password: str = Field(nullable=True)


class Room(RoomBase, table=True):
    id: int = Field(primary_key=True, index=True)
    host: EmailStr = Field(foreign_key='user.email', index=True)
    name: str
    status: RoomStatus = Field(default=RoomStatus.WAITING)
    players: List["Player"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    drawings: List["Drawing"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Player(PlayerBase, table=True):
    id: int = Field(primary_key=True, index=True)
    email: EmailStr = Field(foreign_key='user.email', index=True)
    room_id: int = Field(foreign_key="room.id", index=True)
    room: Room = Relationship(back_populates="players")


class Drawing(DrawingBase, table=True):
    id: int = Field(primary_key=True, index=True)
    room_id: int = Field(foreign_key="room.id", index=True)
    room: Room = Relationship(back_populates="drawings")
