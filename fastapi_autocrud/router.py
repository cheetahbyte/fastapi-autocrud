from fastapi import APIRouter, Depends, Body
from typing import Type, Optional, List
from uuid import UUID

from .storage.base import StorageBackend
from .utils import create_create_model, create_update_model, create_endpoint
from .types import BaseModelType, CreateModelType, UpdateModelType


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


    # GET /
    list_endpoint = create_endpoint(storage.list, dependencies.get("list", []))
    router.get("/", response_model=List[output_model])(list_endpoint)

    # POST /
    async def create_item_endpoint(item: create_model = Body(...), **kwargs):
        return await storage.create(item, **kwargs)

    create_endpoint_with_deps = create_endpoint(create_item_endpoint, dependencies.get("create", []))
    router.post("/", response_model=output_model)(create_endpoint_with_deps)

    get_endpoint = create_endpoint(storage.get, dependencies.get("get", []))
    router.get("/{item_id}", response_model=output_model)(get_endpoint)

    async def update_item_endpoint(item_id: UUID, item: update_model = Body(...), **kwargs):
        return await storage.update(item_id, item, **kwargs)

    update_endpoint_with_deps = create_endpoint(update_item_endpoint, dependencies.get("update", []))
    router.put("/{item_id}", response_model=output_model)(update_endpoint_with_deps)

    delete_endpoint = create_endpoint(storage.delete, dependencies.get("delete", []))
    router.delete("/{item_id}")(delete_endpoint)

    return router