from fastapi import APIRouter
from .users import user_router

all_routers = APIRouter()

all_routers.include_router(user_router, tags=['User'], prefix="/auth")
