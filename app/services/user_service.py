from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repo import UserRepository
from models.user import User
from schemas.user import UserCreate


class UserService:
    def __init__(
        self,
        db: AsyncSession
    ):
        self.db = db
        self.user_repo = UserRepository(db)

    async def create(
        self,
        payload: UserCreate
    ) -> User:
        user = User(
            username = payload.username,
            password_hash = payload.password
        )
        user = await self.user_repo.add(user)
        await self.db.commit()
        return user
