from pydantic import BaseModel
from typing import Optional, Any


class SuccessResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    status: str
    message: str
