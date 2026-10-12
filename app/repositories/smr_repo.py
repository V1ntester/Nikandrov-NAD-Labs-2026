from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.smr import Smr


class SmrRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self,
        smr: Smr
    ) -> Smr:
        self.db.add(smr)
        await self.db.flush()
        await self.db.refresh(smr)
        return smr

    async def get_by_id(
        self,
        smr_id: int
    ) -> Smr | None:
        stmt = (
            select(Smr)
            .where(Smr.id == smr_id)
            .where(Smr.status == "formed")
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_next_by_id(
        self,
        smr_id: int
    ) -> Smr | None:
        stmt = (
            select(Smr)
            .where(Smr.id > smr_id)
            .where(Smr.status == "formed")
            .order_by(Smr.id)
            .limit(1)
        )

        result = await self.db.execute(stmt)
        smr = result.scalar_one_or_none()

        if smr is not None:
            return smr

        stmt = (
            select(Smr)
            .where(Smr.id >= 1)
            .where(Smr.status == "formed")
            .order_by(Smr.id)
            .limit(1)
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
            .limit(1)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_draft(
        self,
        creator_id: int
    ) -> Smr | None:
        stmt = (
            select(Smr)
            .where(Smr.creator_id == creator_id)
            .where(Smr.status == "draft")
            .limit(1)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_formed_with_filters(
        self,
        filter_min: int | None,
        filter_max: int | None
    ) -> list[Smr]:
        stmt = (
            select(Smr)
            .where(Smr.status == "formed")
        )

        if filter_min is not None:
            stmt = stmt.where(Smr.thermal_power >= filter_min)

        if filter_max is not None:
            stmt = stmt.where(Smr.thermal_power <= filter_max)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        smr: Smr
    ) -> Smr:
        self.db.add(smr)
        await self.db.flush()
        return smr
