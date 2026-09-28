from datetime import datetime
from fastapi import APIRouter, Request, Query, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.reactor import Reactor
from models.like import Like


router = APIRouter()
templates = Jinja2Templates(directory="templates")

DEFAULT_IMAGE = "/static/img/DEFAULT-REACTOR.png"
DEFAULT_VIDEO = "/static/img/DEFAULT-REACTOR.mp4"
CURRENT_USER = 1


@router.get("/")
async def get_catalog(
    request: Request,
    thermal_power_min: int = Query(0, ge=0, description="Мин. тепловая мощность"),
    thermal_power_max: int = Query(500, ge=0, description="Макс. тепловая мощность"),
    db: AsyncSession = Depends(get_db),
):

    stmt = (
        select(Reactor)
        .where(Reactor.status == "formed")
        .where(Reactor.thermal_power >= thermal_power_min)
        .where(Reactor.thermal_power <= thermal_power_max)
    )
    result = await db.execute(stmt)
    reactors = result.scalars().all()

    reactor_ids = [r.id for r in reactors]
    likes_map = {}
    if reactor_ids:
        likes_stmt = (
            select(Like.reactor_id, func.count(Like.id))
            .where(Like.reactor_id.in_(reactor_ids))
            .group_by(Like.reactor_id)
        )
        likes_map = dict((await db.execute(likes_stmt)).all())

    return templates.TemplateResponse(
        request=request,
        name="models-grid.html",
        context={
            "reactors": reactors,
            "likes_map": likes_map,
            "default_image": DEFAULT_IMAGE,
            "filter_limits": {"min": thermal_power_min, "max": thermal_power_max},
        },
    )


async def _get_current_draft(db: AsyncSession) -> Reactor | None:
    stmt = (
        select(Reactor)
        .where(Reactor.status == "draft")
        .where(Reactor.creator_id == CURRENT_USER)
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/adding")
async def get_adding(request: Request, db: AsyncSession = Depends(get_db)):
    reactor = await _get_current_draft(db)

    if reactor is None:
        return templates.TemplateResponse(
            request=request,
            name="add-reactor.html",
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name="add-reactor.html",
            context={"reactor": reactor},
        )    


@router.post("/adding")
async def post_adding(
    name: str = Form(...),
    manufacturer: str = Form(...),
    image_url: str = Form(""),
    video_url: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    reactor = await _get_current_draft(db)

    if reactor is None:
        reactor = Reactor(
            name=name,
            manufacturer=manufacturer,
            image_url=image_url or None,
            video_url=video_url or None,
            status="draft",
            creator_id=CURRENT_USER,
        )
        db.add(reactor)
    else:
        reactor.name = name
        reactor.manufacturer = manufacturer
        reactor.image_url = image_url or None
        reactor.video_url = video_url or None

    await db.commit()
    await db.refresh(reactor)

    return RedirectResponse(url="/adding", status_code=303)


@router.post("/adding/publish")
async def post_publish(
    description: str = Form(""),
    thermal_power: int | None = Form(None),
    electrical_power: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    reactor = await _get_current_draft(db)
    if reactor is None:
        raise HTTPException(status_code=404, detail="Draft not found")

    reactor.description = description
    reactor.thermal_power = thermal_power
    reactor.electrical_power = electrical_power
    reactor.status = "formed"
    reactor.formed_at = datetime.utcnow()

    await db.commit()

    return RedirectResponse(url="/", status_code=303)


@router.get("/reactor/{reactor_id}")
async def get_reactor_detail(
    request: Request,
    reactor_id: int,
    next: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Reactor.id)
        .where(Reactor.status == "formed")
        .order_by(Reactor.id)
    )

    result = await db.execute(stmt)
    published_ids = result.scalars().all()

    if next and published_ids:
        current_index = None
        for i, rid in enumerate(published_ids):
            if rid == reactor_id:
                current_index = i
                break

        if current_index is not None and current_index + 1 < len(published_ids):
            next_id = published_ids[current_index + 1]
        else:
            next_id = published_ids[0]

        return RedirectResponse(url=f"/reactor/{next_id}", status_code=303)

    stmt = (
        select(Reactor, func.count(Like.id).label("likes_count")).outerjoin(Like, Like.reactor_id == Reactor.id)
        .where(Reactor.id == reactor_id)
        .where(Reactor.status == "formed")
        .group_by(Reactor.id)
    )
    
    result = await db.execute(stmt)
    row = result.one_or_none()

    if row is None:
        raise HTTPException(status_code=404, detail="Reactor not found")

    reactor, likes_count = row

    return templates.TemplateResponse(
        request=request,
        name="small-modular-reactor.html",
        context={
            "reactor": reactor,
            "likes_count": likes_count,
            "default_video": DEFAULT_VIDEO,
        },
    )


@router.post("/reactor/{reactor_id}/delete")
async def delete_reactor(reactor_id: int, db: AsyncSession = Depends(get_db)):
    update_query = """
        UPDATE reactors
        SET status = 'deleted'
        WHERE id = :id
    """

    await db.execute(text(update_query), {"id": reactor_id})
    await db.commit()

    return RedirectResponse(url="/", status_code=303)
