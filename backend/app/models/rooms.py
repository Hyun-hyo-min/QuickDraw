from enum import Enum
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


class RoomStatus(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"


class RoomBase(SQLModel):
    name: str
    max_players: int = 8


class Room(RoomBase, table=True):
    id: int = Field(primary_key=True)
    host: EmailStr = Field(foreign_key='user.email')
    name: str
    status: RoomStatus = Field(default=RoomStatus.WAITING)
    players: List["Player"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class PlayerBase(SQLModel):
    email: str


class Player(PlayerBase, table=True):
    id: int = Field(primary_key=True)
    email: EmailStr = Field(foreign_key='user.email')
    room_id: int = Field(foreign_key="room.id")
    room: Optional[Room] = Relationship(back_populates="players")
