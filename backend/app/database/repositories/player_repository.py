from fastapi import Depends
from database.repositories.base_repository import BaseRepository
from models.models import Player
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session


class PlayerRepository(BaseRepository[Player]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(Player, session)
