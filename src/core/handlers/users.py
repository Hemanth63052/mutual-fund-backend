from fastapi import status
from fastapi.responses import Response

from src.core.schemas.user import RegisterUser, LoginUser
from src.db.pg.handler import SQLHandler
from src.exceptions import MutualFundException
from src.utils.jwt_util import JWTUtil
from src.utils.password import PasswordHashingUtil


class UserHandler:

    def __init__(self, session):
        self.sql_handler = SQLHandler(session=session)

    async def register_user(self, register_data: RegisterUser):
        """
        Register a new user with the provided registration data.

        :param register_data: Data required for user registration.
        :return: Confirmation message or user details.
        """
        if await self.sql_handler.check_user_exists_by_mail(register_data.email):
            raise MutualFundException(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="User with email already exists"
            )
        register_data.password = PasswordHashingUtil.hash_password(register_data.password)
        await self.sql_handler.insert_new_user(register_data.model_dump())
        return {
            "status": "success",
            "message": "User registered successfully. Please Return Back and Login",
        }

    async def login_user(self, response: Response, login_data: LoginUser):
        """
        Log in a user with the provided login data.

        :param login_data: Data required for user login.
        :param response: fastapi response
        :return: Confirmation message or user details.
        """
        user = await self.sql_handler.check_user_exists_by_mail(login_data.email)
        if not user:
            raise MutualFundException(message="User with this email does not exist.",
                                      code=status.HTTP_404_NOT_FOUND)

        if not PasswordHashingUtil.verify_password(login_data.password, user.password):
            raise MutualFundException(message="Password is invalid",
                                      code=status.HTTP_401_UNAUTHORIZED)
        access_token = JWTUtil.create_access_token({
            "user_id": user.id,
            "email": user.email,
        })
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
        )
        return {
            "status": "success",
            "message": "User logged in successfully.",
            "user_id": user.id,
        }
