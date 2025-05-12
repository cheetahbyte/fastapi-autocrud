from typing import TypeVar, Generic
from pydantic import BaseModel

BaseModelType = TypeVar("BaseModelType", bound=BaseModel)
CreateModelType = TypeVar("CreateModelType", bound=BaseModel)
UpdateModelType = TypeVar("UpdateModelType", bound=BaseModel)
