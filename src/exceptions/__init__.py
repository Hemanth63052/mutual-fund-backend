from fastapi.exceptions import HTTPException
from fastapi import status as fastapi_status
from typing import Optional, TypeVar


T = TypeVar("T")

class MutualFundException(HTTPException):

    code: int = fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR
    status: str = "ERROR"
    message: str | None = status
    data: Optional[T] = None

    def __init__(
            self,
            code: int = 500,
            message: str | None = None,
            data: Optional[T] = None
    ):
        super().__init__(
            status_code=code,
            detail=message
        )
        self.code = code
        self.data = data
        self.message = message
