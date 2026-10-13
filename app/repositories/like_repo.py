from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.like import Like


class LikeRepository:
    def __init__(
        self,
        db: AsyncSession
    ):
        self.db = db

    async def add(
        self,
        like: Like
    ) -> Like:
        self.db.add(like)
        await self.db.flush()
        await self.db.refresh(like)
        return like

    async def get(
        self,
        user_id: int,
        smr_id: int
    ) -> Like | None:
        stmt = (
            select(Like)
            .where(Like.user_id == user_id)
            .where(Like.smr_id == smr_id)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(
            self,
            like: Like
    ) -> None:
        self.db.delete(like)
        await self.db.flush()
