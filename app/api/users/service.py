from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.reactor import Reactor


async def get_draft(db: AsyncSession, creator_id: int) -> Reactor | None:
    stmt = (
        select(Reactor)
        .where(Reactor.creator_id == creator_id)
        .where(Reactor.status == "draft")
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
