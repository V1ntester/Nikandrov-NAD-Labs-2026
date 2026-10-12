from datetime import datetime
from fastapi import APIRouter, Request, Query, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.smr import Smr
from models.like import Like


web_router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

DEFAULT_IMAGE = "/static/img/DEFAULT-SMR.png"
DEFAULT_VIDEO = "/static/img/DEFAULT-SMR.mp4"
CURRENT_USER = 1


@web_router.get("/", include_in_schema=False)
async def get_catalog(
    request: Request,
    thermal_power_min: int = Query(0, ge=0, description="Мин. тепловая мощность"),
    thermal_power_max: int = Query(500, ge=0, description="Макс. тепловая мощность"),
    db: AsyncSession = Depends(get_db),
):

    stmt = (
        select(Smr)
        .where(Smr.status == "formed")
        .where(Smr.thermal_power >= thermal_power_min)
        .where(Smr.thermal_power <= thermal_power_max)
    )
    result = await db.execute(stmt)
    smrs = result.scalars().all()

    smr_ids = [r.id for r in smrs]
    likes_map = {}
    if smr_ids:
        likes_stmt = (
            select(Like.smr_id, func.count(Like.id))
            .where(Like.smr_id.in_(smr_ids))
            .group_by(Like.smr_id)
        )
        likes_map = dict((await db.execute(likes_stmt)).all())

    return templates.TemplateResponse(
        request=request,
        name="smrs-grid.html",
        context={
            "smrs": smrs,
            "likes_map": likes_map,
            "default_image": DEFAULT_IMAGE,
            "filter_limits": {"min": thermal_power_min, "max": thermal_power_max},
        },
    )


async def _get_current_draft(db: AsyncSession) -> Smr | None:
    stmt = (
        select(Smr)
        .where(Smr.status == "draft")
        .where(Smr.creator_id == CURRENT_USER)
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@web_router.get("/adding", include_in_schema=False)
async def get_adding(request: Request, db: AsyncSession = Depends(get_db)):
    smr = await _get_current_draft(db)

    if smr is None:
        return templates.TemplateResponse(
            request=request,
            name="add-smr.html",
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name="add-smr.html",
            context={"smr": smr},
        )    


@web_router.post("/adding", include_in_schema=False)
async def post_adding(
    name: str = Form(...),
    manufacturer: str = Form(...),
    image_url: str = Form(""),
    video_url: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    smr = await _get_current_draft(db)

    if smr is None:
        smr = Smr(
            name=name,
            manufacturer=manufacturer,
            image_url=image_url or None,
            video_url=video_url or None,
            status="draft",
            creator_id=CURRENT_USER,
        )
        db.add(smr)
    else:
        smr.name = name
        smr.manufacturer = manufacturer
        smr.image_url = image_url or None
        smr.video_url = video_url or None

    await db.commit()
    await db.refresh(smr)

    return RedirectResponse(url="/adding", status_code=303)


@web_router.post("/adding/publish", include_in_schema=False)
async def post_publish(
    description: str = Form(""),
    thermal_power: int | None = Form(None),
    electrical_power: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    smr = await _get_current_draft(db)
    if smr is None:
        raise HTTPException(status_code=404, detail="Draft not found")

    smr.description = description
    smr.thermal_power = thermal_power
    smr.electrical_power = electrical_power
    smr.status = "formed"
    smr.formed_at = datetime.utcnow()

    await db.commit()

    return RedirectResponse(url="/", status_code=303)


@web_router.get("/smr/{smr_id}", include_in_schema=False)
async def get_smr_detail(
    request: Request,
    smr_id: int,
    next: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Smr.id)
        .where(Smr.status == "formed")
        .order_by(Smr.id)
    )

    result = await db.execute(stmt)
    published_ids = result.scalars().all()

    if next and published_ids:
        current_index = None
        for i, rid in enumerate(published_ids):
            if rid == smr_id:
                current_index = i
                break

        if current_index is not None and current_index + 1 < len(published_ids):
            next_id = published_ids[current_index + 1]
        else:
            next_id = published_ids[0]

        return RedirectResponse(url=f"/smr/{next_id}", status_code=303)

    stmt = (
        select(Smr, func.count(Like.id).label("likes_count")).outerjoin(Like, Like.smr_id == Smr.id)
        .where(Smr.id == smr_id)
        .where(Smr.status == "formed")
        .group_by(Smr.id)
    )
    
    result = await db.execute(stmt)
    row = result.one_or_none()

    if row is None:
        raise HTTPException(status_code=404, detail="SMR not found")

    smr, likes_count = row

    return templates.TemplateResponse(
        request=request,
        name="smr.html",
        context={
            "smr": smr,
            "likes_count": likes_count,
            "default_video": DEFAULT_VIDEO,
        },
    )


@web_router.post("/smr/{smr_id}/delete", include_in_schema=False)
async def delete_smr(smr_id: int, db: AsyncSession = Depends(get_db)):
    update_query = """
        UPDATE smrs
        SET status = 'deleted'
        WHERE id = :id
    """

    await db.execute(text(update_query), {"id": smr_id})
    await db.commit()

    return RedirectResponse(url="/", status_code=303)
