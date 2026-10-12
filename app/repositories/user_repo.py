from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

class UserRepository:
    def __init__(
        self,
        db: AsyncSession
    ):
        self.db = db

    async def add(
        self,
        user: User
    ) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
