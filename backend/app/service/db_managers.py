import logging
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from models.models import Drawing

logger = logging.getLogger(__name__)


class DBManagerInterface(ABC):
    @abstractmethod
    async def save_drawings(self, drawings: List[Dict], session_id: int, db_session: AsyncSession):
        pass


class DBManager(DBManagerInterface):
    async def save_drawings(self, drawings, session_id, db_session: AsyncSession):
        insert_values = [
            {
                "room_id": session_id,
                "x": drawing_data["x"],
                "y": drawing_data["y"],
                "prev_x": drawing_data["prevX"],
                "prev_y": drawing_data["prevY"]
            }
            for drawing_data in drawings
        ]

        try:
            await db_session.execute(
                Drawing.__table__.insert(),
                insert_values
            )
            await db_session.commit()
        except Exception as e:
            logger.error(f"Error saving draw data to DB: {e}")
            raise


def get_db_manager() -> DBManagerInterface:
    return DBManager()
