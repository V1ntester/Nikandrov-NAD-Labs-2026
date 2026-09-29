from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user import UserCreate


async def create(db: AsyncSession, data: UserCreate):
    user = User(
        username = data.username,
        password_hash = data.password
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
