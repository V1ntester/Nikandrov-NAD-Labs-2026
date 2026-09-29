from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from api.users import service
from models.reactor import Reactor
from schemas.reactor import ReactorOut


router = APIRouter()


@router.get("/users/{user_id}/draft")
async def get_draft(user_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_draft(db, user_id)
