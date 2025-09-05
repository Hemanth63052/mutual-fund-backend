from fastapi import Depends, HTTPException

import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.config import JWTConfig
from src.db.pg.sessions import get_db
from src.db.pg.sql_schemas import Users

security = HTTPBearer()


class ModuleAuthenticationHandler:

    @staticmethod
    async def get_current_user(
            credentials: HTTPAuthorizationCredentials = Depends(security),
            db: Session = Depends(get_db)
    ):
        try:
            payload = jwt.decode(credentials.credentials, JWTConfig.JWT_SECRET_KEY, algorithms=[JWTConfig.JWT_ALGORITHM])
            user_id: str = payload.get("user_id")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
