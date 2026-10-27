from sqlalchemy import select, func, exists
from sqlalchemy.ext.asyncio import AsyncSession

from models.smr import Smr
from models.like import Like


class SmrRepository:
    def __init__(
        self,
        db: AsyncSession
    ):
        self.db = db

    def _likes_count_subquery(self):
        return (
            select(func.count())
            .select_from(Like)
            .where(Like.smr_id == Smr.id)
            .correlate(Smr)
            .scalar_subquery()
        )

    def _is_liked_subquery(self, user_id: int | None):
        if user_id is None:
            return None
        return (
            exists()
            .where(Like.smr_id == Smr.id)
            .where(Like.user_id == user_id)
            .correlate(Smr)
        )

    async def add(
        self,
        smr: Smr
    ) -> Smr:
        self.db.add(smr)
        await self.db.flush()
        await self.db.refresh(smr)
        return smr

    async def update(
        self,
        smr: Smr
    ) -> Smr:
        await self.db.flush()
        await self.db.refresh(smr)
        return smr

    async def get_formed_with_filters(
        self,
        filter_min: int | None,
        filter_max: int | None,
        user_id: int | None = None,
    ) -> list[Smr]:
        likes_count = self._likes_count_subquery().label("likes_count")
        is_liked_expr = self._is_liked_subquery(user_id)

        stmt = select(Smr, likes_count)
        if is_liked_expr is not None:
            stmt = stmt.add_columns(is_liked_expr.label("is_liked"))

        stmt = stmt.where(Smr.status == "formed")
        if filter_min is not None:
            stmt = stmt.where(Smr.thermal_power >= filter_min)
        if filter_max is not None:
            stmt = stmt.where(Smr.thermal_power <= filter_max)

        result = await self.db.execute(stmt)
        rows = result.all()

        out = []
        for row in rows:
            smr = row[0]
            smr.likes_count = row[1] or 0
            smr.is_liked = bool(row[2]) if user_id is not None else False
            out.append(smr)
        return out

    async def get_by_id(
        self,
        smr_id: int,
        user_id: int | None = None,
    ) -> Smr | None:
        likes_count = self._likes_count_subquery().label("likes_count")
        is_liked_expr = self._is_liked_subquery(user_id)

        stmt = select(Smr, likes_count)
        if is_liked_expr is not None:
            stmt = stmt.add_columns(is_liked_expr.label("is_liked"))
        stmt = stmt.where(Smr.id == smr_id)

        result = await self.db.execute(stmt)
        row = result.first()
        if row is None:
            return None

        smr = row[0]
        smr.likes_count = row[1] or 0
        smr.is_liked = bool(row[2]) if user_id is not None else False
        return smr

    async def get_next_by_id(
        self,
        smr_id: int,
        user_id: int | None = None,
    ) -> Smr | None:
        likes_count = self._likes_count_subquery().label("likes_count")
        is_liked_expr = self._is_liked_subquery(user_id)

        stmt = select(Smr, likes_count)
        if is_liked_expr is not None:
            stmt = stmt.add_columns(is_liked_expr.label("is_liked"))
        stmt = (
            stmt
            .where(Smr.id > smr_id)
            .where(Smr.status == "formed")
            .order_by(Smr.id)
            .limit(1)
        )

        result = await self.db.execute(stmt)
        row = result.first()
        if row is None:
            return None

        smr = row[0]
        smr.likes_count = row[1] or 0
        smr.is_liked = bool(row[2]) if user_id is not None else False
        return smr

    async def get_draft(
        self,
        creator_id: int
    ) -> Smr | None:
        stmt = (
            select(Smr)
            .where(Smr.creator_id == creator_id)
            .where(Smr.status == "draft")
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_owned(
        self,
        smr_id: int,
        creator_id: int
    ) -> Smr | None:
        stmt = (
            select(Smr)
            .where(Smr.id == smr_id)
            .where(Smr.creator_id == creator_id)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
