from pydantic import BaseModel, validator


class RegisterUser(BaseModel):
    """
    Schema for registering a new user.
    This schema is used to validate the data when a new user registers.
    """
    email: str
    first_name: str
    last_name: str
    password: str
    phone_number: str | None = None
    address: str | None = None

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class LoginUser(BaseModel):
    """
    Schema for user login.
    This schema is used to validate the data when a user logs in.
    """
    email: str
    password: str
