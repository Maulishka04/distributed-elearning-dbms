"""
Simple Rate Limiting Middleware for FastAPI
Limits requests per IP per time window.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import status
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_buckets = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = int(time.time())
        bucket = self.ip_buckets.get(ip, {"window_start": now, "count": 0})
        if now - bucket["window_start"] > self.window_seconds:
            bucket = {"window_start": now, "count": 0}
        bucket["count"] += 1
        self.ip_buckets[ip] = bucket
        if bucket["count"] > self.max_requests:
            return Response(
                content="Rate limit exceeded. Try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return await call_next(request)
