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
                code=status.HTTP_409_CONFLICT,
                message="User with email already exists"
            )
        register_data.password = PasswordHashingUtil.hash_password(register_data.password)
        user = await self.sql_handler.insert_new_user(register_data)
        await self.sql_handler.upsert_portfolio(user_id=user.id)
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
            raise MutualFundException(message="Invalid Password",
                                      code=status.HTTP_401_UNAUTHORIZED)
        access_token = JWTUtil.create_access_token({
            "user_id": str(user.id),
            "email": str(user.email),
        })
        response.headers['Authorization'] = f"{access_token}"
        response.headers["Access-Control-Expose-Headers"] = "Authorization"
        return {
            "status": "success",
            "message": "User logged in successfully.",
            "user_id": str(user.id),
        }

    async def fetch_user_details(self, user_id: str):
        """
        Fetch user details by user ID.

        :param user_id: The ID of the user to fetch details for.
        :return: User details if found.
        """
        user = await self.sql_handler.fetch_user_by_id(user_id)
        if not user:
            raise MutualFundException(message="User not found.",
                                      code=status.HTTP_404_NOT_FOUND)
        return {
            "status": "success",
            "data": user,
        }
