from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.singleton import CREATOR
from models.reactor import Reactor
from schemas.reactor import ReactorCreate, ReactorPublish
from models.like import Like


async def get_all(db: AsyncSession, filter_min: int | None = None, filter_max: int | None = None) -> list[Reactor]:
    stmt = (
        select(Reactor)
        .where(Reactor.status == "formed")
    )

    if filter_max is not None:
        stmt = stmt.where(Reactor.thermal_power <= filter_max)

    if filter_min is not None:
        stmt = stmt.where(Reactor.thermal_power >= filter_min)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, reactor_id: int) -> Reactor | None:
    stmt = (
        select(Reactor)
        .where(Reactor.id == reactor_id)
        .where(Reactor.status == "formed")
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_next_by_id(db: AsyncSession, reactor_id: int) -> Reactor | None:
    stmt = (
        select(Reactor)
        .where(Reactor.id > reactor_id)
        .where(Reactor.status == "formed")
        .order_by(Reactor.id)
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: ReactorCreate, image_url: str | None = None, video_url: str | None = None) -> Reactor:
    reactor = Reactor(
        name = data.name,
        manufacturer = data.manufacturer,
        image_url = data.image_url,
        video_url = data.video_url,
        creator_id = CREATOR.id
    )

    db.add(reactor)
    await db.commit()
    await db.refresh(reactor)
    return reactor


async def publish(db: AsyncSession, reactor_id: int, creator_id: int, data: ReactorPublish) -> Reactor | None:
    stmt = (
        select(Reactor)
        .where(Reactor.id == reactor_id)
        .where(Reactor.status != "formed")
        .where(Reactor.creator_id != creator_id)
    )

    result = await db.execute(stmt)

    reactor = result.scalar_one_or_none()

    if reactor is None:
        return None

    reactor.description = data.description
    reactor.thermal_power = data.thermal_power
    reactor.electrical_power = data.electrical_power
    reactor.status = "formed"
    reactor.formed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(reactor)
    return reactor


async def delete(db: AsyncSession, reactor_id: int, creator_id: int) -> Reactor | None:
    stmt = (
        select(Reactor)
        .where(Reactor.id == reactor_id)
        .where(Reactor.creator_id == creator_id)
    )

    result = await db.execute(stmt)
    
    reactor = result.scalar_one_or_none()

    if reactor is None:
        return None

    reactor.status = "deleted"

    await db.commit()
    await db.refresh(reactor)
    return reactor


async def like(db: AsyncSession, reactor_id: int, user_id: int) -> Like:
    like = Like(
        user_id = user_id,
        reactor_id = reactor_id
    )

    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like


async def unlike(db: AsyncSession, reactor_id: int, user_id: int) -> Like | None:
    stmt = (
        select(Like)
        .where(Like.reactor_id == reactor_id)
        .where(Like.user_id == user_id)
    )
    
    result = await db.execute(stmt)
    like = result.scalar_one_or_none()

    if like is None:
        return None

    await db.delete(like)
    await db.commit()
    return like
