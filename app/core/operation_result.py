from enum import Enum
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

T = TypeVar("T")


class OperationStatus(str, Enum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    UNAUTHORIZED = "unauthorized"
    INVALID = "invalid"


class OperationResult(Generic[T], BaseModel):
    status: OperationStatus
    data: Optional[T] = None
