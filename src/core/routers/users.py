from fastapi import APIRouter, Depends, Response

from src.core.schemas.user import RegisterUser, LoginUser
from src.core.handlers.users import UserHandler
from src.db.pg.sessions import get_db

user_router = APIRouter(prefix="/users", tags=["Users"], redirect_slashes=True)


@user_router.post("/register", summary="Register a new user")
async def register_user(register_data: RegisterUser, session=Depends(get_db)):
    """
    Endpoint to register a new user.
    This endpoint will handle user registration logic.
    """
    return await UserHandler(session=session).register_user(register_data=register_data)


@user_router.post("/login", summary="User login")
async def login_user(login_data: LoginUser, response: Response, session=Depends(get_db)):
    """
    Endpoint for user login.
    This endpoint will handle user authentication and return a token.
    """
    return await UserHandler(session=session).login_user(response=response, login_data=login_data)
