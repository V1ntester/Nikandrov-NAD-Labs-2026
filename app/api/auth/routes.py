from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from api.auth import service
from models.user import User
from schemas.user import UserCreate, UserOut


router = APIRouter()


@router.post("/auth/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await service.create(db, data)


@router.post("/auth/login")
async def login():
    response = JSONResponse(
        status_code=200,
        content={}
    )

    return response


@router.post("/auth/logout")
async def logout():
    response = JSONResponse(
        status_code=200,
        content={}
    )

    return response