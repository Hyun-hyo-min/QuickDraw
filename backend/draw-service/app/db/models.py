from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Drawing(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4, index=True)
    x: float
    y: float
    prev_x: float
    prev_y: float
    room_id: UUID = Field(index=True)
