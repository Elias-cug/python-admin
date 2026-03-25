from __future__ import annotations

from functools import lru_cache

import redis

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_redis() -> redis.Redis:
    settings = get_settings()
    if not settings.redis_url:
        raise RuntimeError("REDIS_URL is not configured")
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)

