from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy import Column, DateTime


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True)
    name: str
    password: str = Field(nullable=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))