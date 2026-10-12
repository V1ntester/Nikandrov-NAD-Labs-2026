from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from core.singleton import CREATOR
from models.smr import Smr
from models.like import Like
from schemas.smr import SmrCreate, SmrPublish
from repositories.smr_repo import SmrRepository
from repositories.like_repo import LikeRepository


class SmrService:
    def __init__(
        self,
        db: AsyncSession
    ):
        self.db = db
        self.smr_repo = SmrRepository(db)
        self.like_repo = LikeRepository(db)

    async def get_all(
        self,
        filter_min: int | None = None,
        filter_max: int | None = None
    ) -> list[Smr]:
        return await self.smr_repo.get_formed_with_filters(filter_min, filter_max)

    async def get_by_id(
        self,
        smr_id: int
    ) -> Smr | None:
        return await self.smr_repo.get_by_id(smr_id)

    async def get_next_by_id(
        self,
        smr_id: int
    ) -> Smr | None:
        return await self.smr_repo.get_next_by_id(smr_id)

    async def get_draft(
        self,
        creator_id: int
    ) -> Smr | None:
        return await self.smr_repo.get_draft(creator_id)

    async def create(
        self,
        payload: SmrCreate,
        creator_id: int,
        image_url: str | None = None,
        video_url: str | None = None
    ) -> Smr:
        smr = Smr(
            name = payload.name,
            manufacturer = payload.manufacturer,
            image_url = image_url,
            video_url = video_url,
            status = "draft",
            creator_id = creator_id
        )

        smr = await self.smr_repo.add(smr)
        await self.db.commit()
        return smr

    async def publish(
        self,
        payload: SmrPublish,
        creator_id: int
    ) -> Smr | None:
        smr = await self.smr_repo.get_draft(creator_id)

        if smr is None:
            return None

        smr.description = payload.description
        smr.thermal_power = payload.thermal_power
        smr.electrical_power = payload.electrical_power
        smr.status = "formed"
        smr.formed_at = datetime.now(timezone.utc)

        smr = await self.smr_repo.update(smr)
        await self.db.commit()
        return smr

    async def delete(
        self,
        smr_id: int,
        creator_id: int
    ) -> Smr | None:
        smr = await self.smr_repo.get_owned(smr_id, creator_id)

        if smr is not None:
            smr.status = "deleted"
            await self.db.commit()

        return smr

    async def like(
        self,
        user_id: int,
        smr_id: int
    ) -> Like | None:
        smr = await self.smr_repo.get_by_id(smr_id)

        if smr is None or smr.status == "deleted":
            return None

        like = await self.like_repo.get(user_id, smr_id)

        if like is not None:
            return like

        like = Like(
            user_id=user_id,
            smr_id=smr_id
        )

        like = await self.like_repo.add(like)
        await self.db.commit()
        return like

    async def unlike(
        self,
        user_id: int,
        smr_id: int
    ) -> Like | None:
        like = await self.like_repo.get(user_id=user_id, smr_id=smr_id)
        if like is not None:
            await self.like_repo.delete(like)
            await self.db.commit()
        return like
