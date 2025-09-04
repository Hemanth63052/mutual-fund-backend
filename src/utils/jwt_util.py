from src.config import JWTConfig
from datetime import datetime, timedelta, timezone
import jwt


class JWTUtil:

    @staticmethod
    def create_access_token(data: dict) -> str:
        """
        Create a JWT access token with the given data and expiration time.

        Args:
            data (dict): The data to include in the token.

        Returns:
            str: The generated JWT access token.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, JWTConfig.JWT_SECRET_KEY, algorithm=JWTConfig.JWT_ALGORITHM)