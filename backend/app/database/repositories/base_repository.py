from typing import Optional, Any, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from fastapi import Depends
from sqlmodel import SQLModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session

ModelType = TypeVar("ModelType", bound=SQLModel)


class Repository(ABC, Generic[ModelType]):

    @abstractmethod
    async def get_data_by_id(self, id: int) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def get_all_data(self) -> list[ModelType]:
        pass

    @abstractmethod
    async def find_by_filter(self, filters: dict[str, Any]) -> list[ModelType]:
        pass

    @abstractmethod
    async def insert_data(self, data: ModelType) -> None:
        pass

    @abstractmethod
    async def insert_datas(self, datas: list[ModelType]) -> None:
        pass

    @abstractmethod
    async def update_data(self, id: int, data: ModelType) -> None:
        pass

    @abstractmethod
    async def delete_data(self, data: ModelType) -> None:
        pass

    @abstractmethod
    async def delete_data_by_id(self, id: int) -> None:
        pass


class BaseRepository(Repository[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession = Depends(get_db_session)):
        self.model = model
        self.session = session

    async def get_data_by_id(self, id: int) -> Optional[ModelType]:
        return await self.session.get(self.model, id)

    async def get_all_data(self) -> list[ModelType]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def find_by_filter(self, filters: dict[str, Any]) -> list[ModelType]:
        query = select(self.model)
        for attribute, value in filters.items():
            query = query.where(getattr(self.model, attribute) == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def insert_data(self, data: ModelType) -> None:
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)

    async def insert_datas(self, datas: list[ModelType]) -> None:
        self.session.add_all(datas)
        await self.session.commit()

    async def update_data(self, id: int, data: ModelType) -> None:
        db_data = await self.get_data_by_id(id)
        if db_data:
            for key, value in data.dict().items():
                setattr(db_data, key, value)
            await self.session.commit()

    async def delete_data(self, data: ModelType) -> None:
        await self.session.delete(data)
        await self.session.commit()

    async def delete_data_by_id(self, id: int) -> None:
        data = await self.get_data_by_id(id)
        if data:
            await self.delete_data(data)
