from fastapi import APIRouter

from api.v1.smr_router import smr_router
from api.v1.user_router import user_router


api_router = APIRouter(prefix= "/api")

api_router.include_router(smr_router)
api_router.include_router(user_router)
