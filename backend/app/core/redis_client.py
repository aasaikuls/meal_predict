import json
import redis.asyncio as aioredis
from app.core.config import get_settings

_redis_client = None


async def get_redis() -> aioredis.Redis:
    """Return a shared async Redis client (created once)."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


def _session_key(flight_number: str, flight_date: str) -> str:
    return f"session:{flight_number}:{flight_date}"


async def get_session(flight_number: str, flight_date: str) -> dict | None:
    client = await get_redis()
    raw = await client.get(_session_key(flight_number, flight_date))
    return json.loads(raw) if raw else None


async def set_session(flight_number: str, flight_date: str, data: dict) -> None:
    settings = get_settings()
    client = await get_redis()
    await client.setex(
        _session_key(flight_number, flight_date),
        settings.session_ttl_seconds,
        json.dumps(data),
    )


async def update_session(flight_number: str, flight_date: str, data: dict) -> None:
    """Overwrite session data while resetting TTL."""
    await set_session(flight_number, flight_date, data)


async def delete_session(flight_number: str, flight_date: str) -> None:
    client = await get_redis()
    await client.delete(_session_key(flight_number, flight_date))


async def clear_all_sessions() -> None:
    """Delete all session keys (used when user returns to flight selection)."""
    client = await get_redis()
    keys = await client.keys("session:*")
    if keys:
        await client.delete(*keys)
