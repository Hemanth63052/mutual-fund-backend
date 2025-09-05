from pydantic import BaseModel


class SuccessResponseModel(BaseModel):
    status: str = "success"
    message: str | None = None
    data: dict | list | None = None
