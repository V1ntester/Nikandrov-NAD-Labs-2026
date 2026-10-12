from fastapi import APIRouter, HTTPException, Request, Response

from api.v1.dependencies import UserServiceDep, SessionServiceDep
from schemas.user import UserCreate, UserLogin


user_router = APIRouter()


SESSION_COOKIE = "session_id"
SESSION_TTL = 60 * 60 * 24


@user_router.post("/auth/register", summary="Регистрация нового пользователя", tags=["User"])
async def register(
    service: UserServiceDep,
    payload: UserCreate
    ):
    return await service.create(payload)


@user_router.post("/auth/login", summary="Авторизация пользователя", tags=["User"])
async def login(
    payload: UserLogin,
    response: Response,
    service: UserServiceDep,
    sessions: SessionServiceDep
):
    user = await service.authenticate(payload.username, payload.password)

    if user is None:
        raise HTTPException(401)

    session_id = await sessions.create_session(str(user.id))

    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        httponly=True,
        max_age=SESSION_TTL,
        samesite="lax"
    )

    return {
        "id": user.id,
        "username": user.username
    }


@user_router.post("/auth/logout", summary="Выход из аккаунта", tags=["User"])
async def logout(
    request: Request,
    response: Response,
    sessions: SessionServiceDep
):
    session_id = request.cookies.get(SESSION_COOKIE)

    if session_id:
        await sessions.delete_session(session_id)

    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        httponly=True,
        samesite="lax"
    )

    return response
