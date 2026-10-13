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
            password_hash = payload.password,
            role = "guest"
        )
        user = await self.user_repo.add(user)
        await self.db.commit()
        return user

    async def get_by_id(
        self,
        user_id: int
    ) -> User | None:
        return await self.user_repo.get_by_id(user_id)

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self.user_repo.get_by_username(username)
        if user and user.password_hash == password:
            return user
        return None
