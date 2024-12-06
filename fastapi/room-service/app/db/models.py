from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from app.schemas.enums import RoomStatus


class Room(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True)
    name: str
    status: RoomStatus = Field(default=RoomStatus.WAITING)
    max_players: int = 8
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))


class Player(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True)
    room_id: UUID = Field(index=True)
