from typing import Dict, List
from uuid import uuid4
from ..types import BaseModelType, CreateModelType, UpdateModelType
from .base import StorageBackend

class InMemoryStorage(StorageBackend[BaseModelType, CreateModelType, UpdateModelType]):
    def __init__(self):
        self.items: Dict[str, BaseModelType] = {}

    async def list(self) -> List[BaseModelType]:
        return list(self.items.values())

    async def create(self, obj: CreateModelType) -> BaseModelType:
        data = obj.model_dump()
        data["id"] = str(uuid4())
        instance = obj.__class__(**data)  # assumed compatible with BaseModelType
        self.items[data["id"]] = instance
        return instance

    async def get(self, id: str) -> BaseModelType | None:
        return self.items.get(id)

    async def update(self, id: str, obj: UpdateModelType) -> BaseModelType:
        existing = self.items[id]
        updates = obj.model_dump(exclude_unset=True)
        updated = existing.model_copy(update=updates)
        self.items[id] = updated
        return updated

    async def delete(self, id: str) -> None:
        self.items.pop(id, None)
