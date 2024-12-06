from app.db.connection import get_db_session
from uuid import UUID
from abc import ABC, abstractmethod
from typing import Optional, Any, Type, TypeVar, Generic
from fastapi import Depends
from sqlmodel import SQLModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Room, Player
from app.db.connection import get_db_session

ModelType = TypeVar("ModelType", bound=SQLModel)


class Repository(ABC, Generic[ModelType]):

    @abstractmethod
    async def get_all_data(self) -> list[ModelType]:
        pass

    @abstractmethod
    async def get_paginated_data(
        self,
        offset: int,
        limit: int,
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[Any] = None
    ) -> tuple[list[ModelType], int]:
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def find_one_by_filter(self, filters: dict[str, Any]) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def find_all_by_filter(self, filters: dict[str, Any]) -> list[ModelType]:
        pass

    @abstractmethod
    async def insert_data(self, data: ModelType) -> None:
        pass

    @abstractmethod
    async def insert_datas(self, datas: list[ModelType]) -> None:
        pass

    @abstractmethod
    async def update_data(self, id: UUID, data: ModelType) -> None:
        pass

    @abstractmethod
    async def delete_data(self, data: ModelType) -> None:
        pass

    @abstractmethod
    async def delete_data_by_id(self, id: UUID) -> None:
        pass


class BaseRepository(Repository[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_all_data(self) -> list[ModelType]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get_paginated_data(
        self,
        offset: int,
        limit: int,
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[Any] = None
    ) -> tuple[list[ModelType], int]:
        query = select(self.model)

        if filters:
            for attribute, value in filters.items():
                query = query.where(getattr(self.model, attribute) == value)

        if order_by:
            query = query.order_by(order_by)

        total_result = await self.session.execute(query)
        total_count = len(total_result.scalars().all())

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)

        return result.scalars().all(), total_count

    async def find_by_id(self, id: UUID) -> Optional[ModelType]:
        return await self.session.get(self.model, id)

    async def find_one_by_filter(self, filters: dict[str, Any]) -> Optional[ModelType]:
        query = select(self.model)
        for attribute, value in filters.items():
            query = query.where(getattr(self.model, attribute) == value)
        result = await self.session.execute(query)
        return result.scalar()

    async def find_all_by_filter(self, filters: dict[str, Any]) -> list[ModelType]:
        query = select(self.model)
        for attribute, value in filters.items():
            query = query.where(getattr(self.model, attribute) == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def insert_data(self, data: ModelType) -> None:
        self.session.add(data)
        await self.session.commit()

    async def insert_datas(self, datas: list[ModelType]) -> None:
        self.session.add_all(datas)
        await self.session.commit()

    async def update_data(self, id: UUID, data: ModelType) -> None:
        db_data = await self.find_by_id(id)
        if db_data:
            for key, value in data.dict().items():
                setattr(db_data, key, value)
            await self.session.commit()

    async def delete_data(self, data: ModelType) -> None:
        await self.session.delete(data)
        await self.session.commit()

    async def delete_data_by_id(self, id: UUID) -> None:
        data = await self.find_by_id(id)
        if data:
            await self.delete_data(data)


class RoomRepository(BaseRepository[Room]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(Room, session)


class PlayerRepository(BaseRepository[Player]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(Player, session)
