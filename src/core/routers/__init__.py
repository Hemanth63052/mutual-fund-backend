from fastapi import APIRouter, Depends
from .users import user_router
from .rapidapi import rapidapi_router
from ..handlers.auth import ModuleAuthenticationHandler

all_routers = APIRouter(prefix="/api")

all_routers.include_router(user_router, tags=['User'])
all_routers.include_router(rapidapi_router, tags=['RapidAPI'], dependencies=[Depends(ModuleAuthenticationHandler.get_current_user)])
