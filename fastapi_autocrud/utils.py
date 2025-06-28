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

    # 1. Define the generic endpoint function.
    async def endpoint(**kwargs):
        # This function simply passes all resolved arguments (path params and
        # dependencies) from FastAPI directly to your storage method.
        return await storage_func(**kwargs)

    # 2. Get the base signature from the storage function or its wrapper.
    storage_sig = inspect.signature(storage_func)
    params = list(storage_sig.parameters.values())

    # 3. Add the dependencies to the signature's parameters.
    for dep in route_dependencies:
        dep_func = dep.dependency
        param_name = dep_func.__name__

        # ========================== THE FIX IS HERE ==========================
        # We create the parameter but explicitly set its annotation to empty.
        # This prevents the ORM model type hint (e.g., '-> User') from being
        # part of the function signature that FastAPI analyzes.
        # FastAPI only needs the `default=Depends(...)` part to work correctly.
        params.append(
            inspect.Parameter(
                name=param_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=dep,
                annotation=inspect.Parameter.empty  # This line solves the error
            )
        )
        # =====================================================================

    # 4. Create the new signature from our combined list of parameters.
    sig = inspect.Signature(params)

    # 5. Apply the new signature to our endpoint function.
    endpoint.__signature__ = sig

    # Give the function a name for better debugging.
    endpoint.__name__ = storage_func.__name__

    return endpoint
