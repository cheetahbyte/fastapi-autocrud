from pydantic import BaseModel, create_model
from typing import Optional, Any, Dict
import inspect

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


def create_endpoint(storage_func, route_dependencies):
    """
    A factory to create a FastAPI endpoint with dynamic dependencies,
    stripping all non-Pydantic type hints from the final signature.
    """

    async def endpoint(**kwargs):
        return await storage_func(**kwargs)

    storage_sig = inspect.signature(storage_func)

    # === START: The Final Fix ===
    # We will rebuild ALL parameters to ensure their annotations are stripped.
    final_params = []

    # 1. Process base parameters from the original storage function (like 'user').
    for param in storage_sig.parameters.values():
        # Ignore 'self', 'kwargs', etc.
        if param.name in ['self', 'obj', 'kwargs']:
            continue

        # Rebuild the parameter, but explicitly set annotation to empty.
        # This strips problematic hints like 'user: User'.
        final_params.append(
            inspect.Parameter(
                name=param.name,
                kind=param.kind,
                default=param.default,
                annotation=inspect.Parameter.empty
            )
        )

    # 2. Process dependency parameters (like 'get_current_user').
    for dep in route_dependencies:
        final_params.append(
            inspect.Parameter(
                name=dep.dependency.__name__,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=dep,
                annotation=inspect.Parameter.empty
            )
        )
    # === END: The Final Fix ===

    # 3. Create and apply the fully sanitized signature.
    endpoint.__signature__ = inspect.Signature(final_params)
    endpoint.__name__ = storage_func.__name__

    return endpoint