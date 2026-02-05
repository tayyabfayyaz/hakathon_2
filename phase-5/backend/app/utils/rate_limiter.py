"""Rate limiter utilities using Redis."""

import time
import logging
from typing import Optional

import redis.asyncio as redis
from app.config import get_settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter using Redis."""

    def __init__(self):
        settings = get_settings()
        self.redis_client = redis.from_url(settings.redis_url)

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int, float]:
        """
        Check if a request is allowed based on rate limits.

        Args:
            key: Unique identifier for the rate limit (e.g., user_id or IP)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        current_time = time.time()
        pipeline = self.redis_client.pipeline()

        # Calculate the start of the current window
        window_start = current_time - (current_time % window_seconds)
        window_end = window_start + window_seconds

        # Clean up old entries and get current count
        pipeline.zremrangebyscore(key, 0, window_start)
        pipeline.zcard(key)
        pipeline.expire(key, window_seconds * 2)  # Expire after 2 windows

        results = await pipeline.execute()
        current_count = results[1]

        is_allowed = current_count < max_requests

        if is_allowed:
            # Add the current request to the window
            await self.redis_client.zadd(key, {str(current_time): current_time})

        remaining = max(0, max_requests - current_count - (0 if is_allowed else 1))
        reset_time = window_end

        return is_allowed, remaining, reset_time

# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    """Get or create the rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter