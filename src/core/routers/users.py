from fastapi import APIRouter, Depends, Response

from src.core.schemas.user import RegisterUser, LoginUser
from src.core.handlers.users import UserHandler
from src.db.pg.sessions import get_db
from ..handlers.auth import ModuleAuthenticationHandler

user_router = APIRouter()


@user_router.post("/auth/register", summary="Register a new user")
async def register_user(register_data: RegisterUser, session=Depends(get_db)):
    """
    Endpoint to register a new user.
    This endpoint will handle user registration logic.
    """
    return await UserHandler(session=session).register_user(register_data=register_data)


@user_router.post("/auth/login", summary="User login")
async def login_user(login_data: LoginUser, response: Response, session=Depends(get_db)):
    """
    Endpoint for user login.
    This endpoint will handle user authentication and return a token.
    """
    return await UserHandler(session=session).login_user(response=response, login_data=login_data)

@user_router.get("/me", summary="Get current user")
async def get_current_user(user=Depends(ModuleAuthenticationHandler.get_current_user), session=Depends(get_db)):
    """
    Endpoint to get the current logged-in user's details.
    This endpoint requires authentication.
    """
    return await UserHandler(session=session).fetch_user_details(user.id)

@user_router.post("/logout", summary="User logout")
async def logout_user(response: Response):
    """
    Endpoint for user logout.
    This endpoint will clear the authentication token.
    """
    response.delete_cookie(key="access_token")
    return {
        "status": "success",
        "message": "User logged out successfully.",
    }
