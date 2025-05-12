from typing import Type, List, Optional
from tortoise.models import Model as TortoiseModel
from tortoise.queryset import QuerySet
from ..types import BaseModelType, CreateModelType, UpdateModelType
from .base import StorageBackend


class TortoiseStorage(StorageBackend[BaseModelType, CreateModelType, UpdateModelType]):
    def __init__(self, db_model: Type[TortoiseModel], output_model: Type[BaseModelType]):
        self.db_model = db_model
        self.output_model = output_model

    async def list(self) -> List[BaseModelType]:
        objs = await self.db_model.all()
        return [self.output_model.model_validate(obj) for obj in objs]

    async def create(self, obj: CreateModelType) -> BaseModelType:
        db_obj = await self.db_model.create(**obj.model_dump())
        return self.output_model.model_validate(db_obj)

    async def get(self, id: str) -> Optional[BaseModelType]:
        obj = await self.db_model.get_or_none(id=id)
        if obj:
            return self.output_model.model_validate(obj)
        return None

    async def update(self, id: str, obj: UpdateModelType) -> BaseModelType:
        db_obj = await self.db_model.get(id=id)
        for field, value in obj.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        await db_obj.save()
        return self.output_model.model_validate(db_obj)

    async def delete(self, id: str) -> None:
        await self.db_model.filter(id=id).delete()
