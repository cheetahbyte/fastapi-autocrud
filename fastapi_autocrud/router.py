from fastapi import APIRouter, Depends, Body
from typing import Type, Optional, List
from uuid import UUID

from .storage.base import StorageBackend
from .utils import create_create_model, create_update_model
from .types import BaseModelType, CreateModelType, UpdateModelType
import asyncio

def generate_crud_router(
    output_model: Type[BaseModelType],
    create_model: Optional[CreateModelType] = None,
    update_model: Optional[UpdateModelType] = None,
    storage: StorageBackend = None,
    dependencies: dict[str, List[Depends]] = None,
) -> APIRouter:
    create_model = create_model or create_create_model(output_model)
    update_model = update_model or create_update_model(output_model)
    dependencies = dependencies or {}

    router = APIRouter()

    def extract_dependencies(deps: list[Depends]):
        return [dep.depdency for dep in deps]

    async def resolve_dependencies(deps: list):
        results = await asyncio.gather(*[dep() for dep in deps])
        return results

    async def call_storage_with_deps(func, *args, route_name=None, **kwargs):
        deps = extract_dependencies(dependencies.get(route_name, []))
        values = await resolve_dependencies(deps)
        dep_names = [d.__name__ for d in deps]
        return await func(*args, **kwargs, **dict(zip(dep_names, values)))

    # Routes
    @router.get("/", response_model=List[output_model])
    async def list_items():
        return await call_storage_with_deps(storage.list, route_name="list")

    @router.post("/", response_model=output_model)
    async def create_item(item: create_model = Body(...)):
        return await call_storage_with_deps(storage.create, item, route_name="create")

    @router.get("/{item_id}", response_model=output_model)
    async def get_item(item_id: UUID):
        return await call_storage_with_deps(storage.get, item_id, route_name="get")

    @router.put("/{item_id}", response_model=output_model)
    async def update_item(item_id: UUID, item: update_model = Body(...)):
        return await call_storage_with_deps(storage.update, item_id, item, route_name="update")

    @router.delete("/{item_id}")
    async def delete_item(item_id: UUID):
        return await call_storage_with_deps(storage.delete, item_id, route_name="delete")

    return router