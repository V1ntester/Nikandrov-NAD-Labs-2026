from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.user_service import UserService
from schemas.user import UserCreate


user_router = APIRouter()


def get_user_service(
    db: AsyncSession = Depends(get_db)
) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@user_router.post("/auth/register", summary="Регистрация нового пользователя", tags=["User"])
async def register(
    service: UserServiceDep,
    payload: UserCreate
    ):
    return await service.create(payload)


@user_router.post("/auth/login", summary="Авторизация пользователя", tags=["User"])
async def login():
    response = JSONResponse(
        status_code=200,
        content={}
    )

    return response


@user_router.post("/auth/logout", summary="Выход из аккаунта", tags=["User"])
async def logout():
    response = JSONResponse(
        status_code=200,
        content={}
    )

    return response
