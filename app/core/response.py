from typing import Generic, TypeVar, Optional, Dict, Any

from pydantic import BaseModel, model_serializer

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    code: int = 200
    message: str = "Success"
    data: Optional[T] = None

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        result = {
            "code": self.code,
            "message": self.message
        }
        if self.data is not None:
            result["data"] = self.data
        return result
