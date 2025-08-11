from typing import Generic, TypeVar, List

from pydantic import BaseModel

T = TypeVar("T")


class PagingData(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
