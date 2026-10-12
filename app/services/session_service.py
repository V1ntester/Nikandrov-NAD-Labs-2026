import secrets

from redis.asyncio import Redis


SESSION_TTL = 60 * 60 * 24 


class SessionService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def create_session(self, user_id: str) -> str:
        session_id = secrets.token_urlsafe(32)

        await self.redis.set(
            f"session:{session_id}",
            user_id,
            ex=SESSION_TTL,
        )

        return session_id

    async def get_user_id(
        self,
        session_id: str,
    ) -> str | None:
        return await self.redis.get(
            f"session:{session_id}"
        )

    async def delete_session(
        self,
        session_id: str,
    ) -> None:
        await self.redis.delete(
            f"session:{session_id}"
        )
