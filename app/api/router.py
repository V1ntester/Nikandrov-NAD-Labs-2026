from fastapi import APIRouter

from api.reactors.routes import router as reactors_router
from api.users.routes import router as users_router
from api.auth.routes import router as auth_router


api_router = APIRouter(prefix= "/api")

api_router.include_router(reactors_router)
api_router.include_router(users_router)
api_router.include_router(auth_router)