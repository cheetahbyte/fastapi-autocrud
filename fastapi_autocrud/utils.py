from pydantic import BaseModel, create_model
from typing import Optional, Any, Dict


def create_create_model(base: type[BaseModel]) -> type[BaseModel]:
    fields: Dict[str, tuple[Any, Any]] = {}
    for name, field in base.model_fields.items():
        if name == "id":
            continue
        fields[name] = (field.annotation, ...)
    return create_model(f"{base.__name__}Create", **fields)


def create_update_model(base: type[BaseModel]) -> type[BaseModel]:
    fields: Dict[str, tuple[Any, Any]] = {}
    for name, field in base.model_fields.items():
        if name == "id":
            continue
        fields[name] = (Optional[field.annotation], None)
    return create_model(f"{base.__name__}Update", **fields)


import inspect
from functools import wraps


def create_endpoint(storage_func, route_dependencies):
    """
    A factory to create a FastAPI endpoint with dynamic dependencies in its signature.
    """
    async def endpoint(**kwargs):
        path_params = {
            p.name: kwargs.pop(p.name)
            for p in sig.parameters.values()
            if p.kind == p.POSITIONAL_OR_KEYWORD and p.name in kwargs
        }
        return await storage_func(**path_params, **kwargs)

    storage_sig = inspect.signature(storage_func)
    params = [p for p in storage_sig.parameters.values() if p.name not in ['self', 'obj', 'kwargs']]

    for dep in route_dependencies:
        dep_func = dep.dependency
        param_name = dep_func.__name__
        params.append(
            inspect.Parameter(
                name=param_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=dep
            )
        )

    sig = inspect.Signature(params)
    endpoint.__signature__ = sig
    endpoint.__name__ = storage_func.__name__

    return endpoint
