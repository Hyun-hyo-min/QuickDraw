from fastapi import Depends
from database.repositories.base_repository import BaseRepository
from models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(User, session)
