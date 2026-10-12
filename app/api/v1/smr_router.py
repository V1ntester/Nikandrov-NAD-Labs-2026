from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.singleton import CREATOR
from db.session import get_db
from services.smr_service import SmrService
from storage.service import upload_file
from schemas.smr import SmrCreate, SmrPublish, SmrLike


smr_router = APIRouter()


def get_smr_service(
    db: AsyncSession = Depends(get_db)
) -> SmrService:
    return SmrService(db)


SmrServiceDep = Annotated[SmrService, Depends(get_smr_service)]


@smr_router.get("/smrs", summary="Получить список СМР с фильтрацией по цене", tags=["SMR"])
async def get_smrs(
    service: SmrServiceDep,
    filter_min: int | None = None,
    filter_max: int | None = None
):
    smrs = await service.get_all(filter_min, filter_max)
    return {"smrs": smrs}


@smr_router.get("/smrs/draft", summary="Получить черновик текущего пользователя", tags=["SMR"])
async def get_draft(
    service: SmrServiceDep,
):
    smr = await service.get_draft(CREATOR.id)
    if smr is None:
        raise HTTPException(404)
    return smr


@smr_router.get("/smrs/{smr_id}", summary="Получить СМР по ID", tags=["SMR"])
async def get_smr(
    service: SmrServiceDep,
    smr_id: int,
    select_next: bool = False
):
    smr = await (service.get_next_by_id(smr_id) if select_next
                 else service.get_by_id(smr_id))
    if smr is None:
        raise HTTPException(404)
    return smr


@smr_router.post("/smrs", summary="Создать новый СМР с изображением и видео", tags=["SMR"])
async def create_smr(
    service: SmrServiceDep,
    name: str = Form(...),
    manufacturer: str = Form(...),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
):
    image_url = None
    video_url = None

    if image:
        image_url = await upload_file(
            image,
            "smrs/images",
        )

    if video:
        video_url = await upload_file(
            video,
            "smrs/videos",
        )

    smr = SmrCreate(
        name=name,
        manufacturer=manufacturer,
    )

    smr = await service.create(smr, CREATOR.id, image_url, video_url)
    return smr


@smr_router.put("/smrs/draft/publish", summary="Опубликовать черновик СМР", tags=["SMR"])
async def publish_smr(
    service: SmrServiceDep,
    payload: SmrPublish
):
    smr = await service.publish(payload, CREATOR.id)
    if smr is None:
        raise HTTPException(404)
    return smr


@smr_router.delete("/smrs/{smr_id}", summary="Удалить СМР по ID", tags=["SMR"])
async def delete_smr(
    service: SmrServiceDep,
    smr_id: int,
):
    smr = await service.delete(smr_id, CREATOR.id)
    if smr is None:
        raise HTTPException(404)
    return smr


@smr_router.post("/smrs/{smr_id}/like", summary="Поставить или убрать лайк СМР", tags=["SMR"])
async def like_smr(
    service: SmrServiceDep,
    smr_id: int,
    payload: SmrLike
):
    result = await (service.like(CREATOR.id, smr_id) if payload.action
                    else service.unlike(CREATOR.id, smr_id))
    if result is None:
        raise HTTPException(404)
    return result
