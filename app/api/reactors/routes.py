from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from core.singleton import CREATOR
from db.session import get_db
from api.reactors import service
from storage.service import upload_file
from models.reactor import Reactor
from schemas.reactor import ReactorCreate, ReactorOut, ReactorListResponse, ReactorPublish, ReactorLike


router = APIRouter()


@router.get("/reactors")
async def get_reactors(filter_min: int = None, filter_max: int = None, db: AsyncSession = Depends(get_db)):
    reactors = await service.get_all(db, filter_min, filter_max);
    return {"reactors": reactors}


@router.get("/reactors/{reactor_id}")
async def get_reactor(reactor_id: int, next: bool, db: AsyncSession = Depends(get_db)):
    if next:
        reactor = await service.get_next_by_id(db, reactor_id)
    else:
        reactor = await service.get_by_id(db, reactor_id)
    return reactor


@router.post("/reactors")
async def create_reactor(
    name: str = Form(...),
    manufacturer: str = Form(...),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db)
):
    image_url = None
    video_url = None

    if image:
        image_url = await upload_file(
            image,
            "reactors/images",
        )

    if video:
        video_url = await upload_file(
            video,
            "reactors/videos",
        )

    reactor = ReactorCreate(
        name=name,
        manufacturer=manufacturer,
        image_url=image_url,
        video_url=video_url
    )

    reactor = await service.create(db, reactor)
    return reactor 


@router.put("/reactors/{reactor_id}/publish")
async def publish_reactor(reactor_id: int, data: ReactorPublish, db: AsyncSession = Depends(get_db)):
    return await service.publish(db, reactor_id, CREATOR.id, data)


@router.delete("/reactors/{reactor_id}")
async def delete_reactor(reactor_id: int, db: AsyncSession = Depends(get_db)):
    return await service.delete(db, reactor_id, CREATOR.id)


@router.post("/reactors/{reactor_id}/like")
async def like_reactor(reactor_id: int, data: ReactorLike, db: AsyncSession = Depends(get_db)):
    if data.action:
        return await service.like(db, reactor_id, CREATOR.id)
    else:
        return await service.unlike(db, reactor_id, CREATOR.id)
    