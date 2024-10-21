from typing import Optional
from pydantic import BaseSettings
from sqlmodel import SQLModel, create_engine, Session
from config import settings

database_connection_string = settings.DATABASE_URL
engine = create_engine(database_connection_string, echo=True)

def conn():
	SQLModel.metadata.create_all(engine)

def get_session():
	with Session(engine) as session:
		yield session
