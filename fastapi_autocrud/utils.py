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
