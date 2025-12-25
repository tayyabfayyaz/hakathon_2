"""Rate limiting middleware for auth endpoints.

Implements a simple in-memory rate limiter with configurable limits.
For production, consider using Redis for distributed rate limiting.
"""
import time
from collections import defaultdict
from typing import Callable, Dict, Tuple

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        # Dict[client_key, list of request timestamps]
        self._requests: Dict[str, list] = defaultdict(list)

    def _get_client_key(self, request: Request) -> str:
        """Get a unique key for the client."""
        # Use X-Forwarded-For if behind a proxy, otherwise client host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        return client_ip

    def _cleanup_old_requests(self, key: str, current_time: float) -> None:
        """Remove requests outside the current window."""
        cutoff = current_time - self.window_seconds
        self._requests[key] = [
            ts for ts in self._requests[key] if ts > cutoff
        ]

    def is_allowed(self, request: Request) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time.time()
        key = self._get_client_key(request)

        # Clean up old requests
        self._cleanup_old_requests(key, current_time)

        # Check rate limit
        request_count = len(self._requests[key])
        remaining = max(0, self.requests_per_minute - request_count)

        if request_count >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for {key}",
                extra={"client_ip": key, "requests": request_count},
            )
            return False, 0

        # Record this request
        self._requests[key].append(current_time)
        return True, remaining - 1

    def get_retry_after(self, request: Request) -> int:
        """Get seconds until rate limit resets."""
        key = self._get_client_key(request)
        if not self._requests[key]:
            return 0
        oldest_request = min(self._requests[key])
        retry_after = int(oldest_request + self.window_seconds - time.time())
        return max(1, retry_after)


# Global rate limiter for auth endpoints
auth_rate_limiter = RateLimiter(requests_per_minute=10)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to specific endpoints."""

    def __init__(
        self,
        app,
        rate_limiter: RateLimiter = None,
        paths: list[str] = None,
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter or auth_rate_limiter
        self.paths = paths or ["/api/v1/auth/login", "/api/v1/auth/register"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only rate limit specific paths
        if request.url.path not in self.paths:
            return await call_next(request)

        is_allowed, remaining = self.rate_limiter.is_allowed(request)

        if not is_allowed:
            retry_after = self.rate_limiter.get_retry_after(request)
            return Response(
                content='{"error_code": "RATE_LIMITED", "message": "Too many requests. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


def rate_limit_auth(request: Request) -> None:
    """
    Dependency for rate limiting auth endpoints.

    Usage:
        @router.post("/login")
        async def login(request: Request, _: None = Depends(rate_limit_auth)):
            ...
    """
    is_allowed, remaining = auth_rate_limiter.is_allowed(request)
    if not is_allowed:
        retry_after = auth_rate_limiter.get_retry_after(request)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": "RATE_LIMITED",
                "message": "Too many requests. Please try again later.",
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Remaining": "0",
            },
        )
