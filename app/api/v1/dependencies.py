from typing import Annotated

from fastapi import Depends, HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.redis import get_redis
from services.session_service import SessionService
from services.user_service import UserService
from models.user import User


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(db)


def get_session_service(
    redis_client: Redis = Depends(get_redis),
) -> SessionService:
    return SessionService(redis_client)


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]

SessionServiceDep = Annotated[
    SessionService,
    Depends(get_session_service),
]


async def get_current_user(
    request: Request,
    service: UserServiceDep,
    sessions: SessionServiceDep,
) -> User:
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(401)

    user_id = await sessions.get_user_id(session_id)

    if user_id is None:
        raise HTTPException(401)

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        await sessions.delete_session(session_id)
        raise HTTPException(401)

    user = await service.get_by_id(user_id_int)

    if user is None:
        await sessions.delete_session(session_id)
        raise HTTPException(401)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_optional(
    request: Request,
    service: UserServiceDep,
    sessions: SessionServiceDep,
) -> User | None:
    session_id = request.cookies.get("session_id")

    if not session_id:
        return None

    user_id = await sessions.get_user_id(session_id)

    if user_id is None:
        return None

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        await sessions.delete_session(session_id)
        return None

    user = await service.get_by_id(user_id_int)

    if user is None:
        await sessions.delete_session(session_id)
        return None

    return user


CurrentUserOptional = Annotated[
    User | None,
    Depends(get_current_user_optional),
]


def require_role(role: str):
    async def role_checker(current_user: CurrentUser) -> User:
        if current_user.role != role:
            raise HTTPException(403)
        return current_user
    return role_checker


CreatorUser = Annotated[User, Depends(require_role("creator"))]
