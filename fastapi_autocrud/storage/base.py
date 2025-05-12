from abc import ABC, abstractmethod
from typing import Generic, List
from ..types import BaseModelType, CreateModelType, UpdateModelType

class StorageBackend(ABC, Generic[BaseModelType, CreateModelType, UpdateModelType]):
    @abstractmethod
    async def list(self, **kwargs) -> List[BaseModelType]: ...

    @abstractmethod
    async def create(self, obj: CreateModelType, **kwargs) -> BaseModelType: ...

    @abstractmethod
    async def get(self, id: str, **kwargs) -> BaseModelType | None: ...

    @abstractmethod
    async def update(self, id: str, obj: UpdateModelType, **kwargs) -> BaseModelType: ...

    @abstractmethod
    async def delete(self, id: str, **kwargs) -> None: ...
