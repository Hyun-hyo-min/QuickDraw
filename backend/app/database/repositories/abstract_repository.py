from abc import ABC, abstractmethod
from typing import Optional, Any
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession


class Repository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    def get_data_by_id(self, id: int) -> Optional[SQLModel]:
        pass

    @abstractmethod
    def get_all_data(self) -> list[SQLModel]:
        pass

    @abstractmethod
    def find_by_filter(self, filters: dict[str, Any]) -> list[SQLModel]:
        pass

    @abstractmethod
    def insert_data(self, data: SQLModel) -> None:
        pass

    @abstractmethod
    def insert_datas(self, datas: list[SQLModel]) -> None:
        pass

    @abstractmethod
    def update_data(self, id: int, data: SQLModel) -> None:
        pass

    @abstractmethod
    def delete_data(self, data: SQLModel) -> None:
        pass

    @abstractmethod
    def delete_data_by_id(self, id: int) -> None:
        pass

    @abstractmethod
    def start_transaction(self) -> None:
        pass

    @abstractmethod
    def commit_transaction(self) -> None:
        pass

    @abstractmethod
    def rollback_transaction(self) -> None:
        pass
