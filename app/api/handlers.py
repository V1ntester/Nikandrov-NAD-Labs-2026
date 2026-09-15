from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from data.collections import reactors_db
from fastapi.responses import RedirectResponse


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def get_catalog(request: Request, thermal_power_from_param: str | None = None):
    thermal_power_from = int(thermal_power_from_param) if thermal_power_from_param else None

    if thermal_power_from is not None:
        filtered = [r for r in reactors_db if r["thermal_power"] >= thermal_power_from and r["status"] == "published"]
    else:
        filtered = [r for r in reactors_db if r["status"] == "published"]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"reactors": filtered}
    )


@router.get("/adding")
def get_adding(request: Request):
    reactor = next((r for r in reactors_db if r["status"] == "draft"), None)

    return templates.TemplateResponse(
        request=request,
        name="adding.html",
        context={"reactor": reactor}
    )


@router.get("/reactor/{reactor_id}")
def get_reactor_detail(request: Request, reactor_id: int, next: bool | None = None):
    published_sorted = sorted(
        (r for r in reactors_db if r["status"] == "published"),
        key=lambda r: r["id"]
    )

    current_index = None
    for i, r in enumerate(published_sorted):
        if r["id"] == reactor_id:
            current_index = i
            break

    if next and published_sorted:
        if current_index is not None and current_index + 1 < len(published_sorted):
            next_reactor = published_sorted[current_index + 1]
        else:
            next_reactor = published_sorted[0]
        return RedirectResponse(url=f"/reactor/{next_reactor['id']}", status_code=303)

    reactor = None
    for r in reactors_db:
        if r["id"] == reactor_id and r["status"] == "published":
            reactor = r
            break

    return templates.TemplateResponse(
        request=request,
        name="reactor.html",
        context={"reactor": reactor}
    )