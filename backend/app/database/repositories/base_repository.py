from typing import Optional, Any, List, Dict
from abc import ABC, abstractmethod
from fastapi import Depends
from sqlmodel import SQLModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session


class Repository(ABC):

    @abstractmethod
    async def get_data_by_id(self, id: int) -> Optional[SQLModel]:
        pass

    @abstractmethod
    async def get_all_data(self) -> List[SQLModel]:
        pass

    @abstractmethod
    async def find_by_filter(self, filters: Dict[str, Any]) -> List[SQLModel]:
        pass

    @abstractmethod
    async def insert_data(self, data: SQLModel) -> None:
        pass

    @abstractmethod
    async def insert_datas(self, datas: List[SQLModel]) -> None:
        pass

    @abstractmethod
    async def update_data(self, id: int, data: SQLModel) -> None:
        pass

    @abstractmethod
    async def delete_data(self, data: SQLModel) -> None:
        pass

    @abstractmethod
    async def delete_data_by_id(self, id: int) -> None:
        pass


class BaseRepository(Repository):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_data_by_id(self, id: int) -> Optional[SQLModel]:
        return await self.session.get(SQLModel, id)

    async def get_all_data(self) -> List[SQLModel]:
        result = await self.session.execute(select(SQLModel))
        return result.scalars().all()

    async def find_by_filter(self, filters: Dict[str, Any]) -> List[SQLModel]:
        query = select(SQLModel)
        for attribute, value in filters.items():
            query = query.where(getattr(SQLModel, attribute) == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def insert_data(self, data: SQLModel) -> None:
        self.session.add(data)
        await self.session.commit()

    async def insert_datas(self, datas: List[SQLModel]) -> None:
        self.session.add_all(datas)
        await self.session.commit()

    async def update_data(self, id: int, data: SQLModel) -> None:
        db_data = await self.get_data_by_id(id)
        if db_data:
            for key, value in data.dict().items():
                setattr(db_data, key, value)
            await self.session.commit()

    async def delete_data(self, data: SQLModel) -> None:
        await self.session.delete(data)
        await self.session.commit()

    async def delete_data_by_id(self, id: int) -> None:
        data = await self.get_data_by_id(id)
        if data:
            await self.delete_data(data)
