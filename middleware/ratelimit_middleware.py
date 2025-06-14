from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from config.settings import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter per API key or IP."""

    def __init__(self, app):  # type: ignore[no-untyped-def]
        super().__init__(app)
        settings = get_settings()
        parsed = settings.parsed_rate_limit
        if parsed is None:
            self.max_req = 0
            self.window = 0
        else:
            self.max_req, self.window = parsed

        # key -> deque[timestamps]
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if self.max_req == 0:
            # Disabled
            return await call_next(request)

        now = time.time()

        # Identify client: API key or IP.
        token = request.headers.get("authorization") or request.headers.get("x-api-key")
        if token and token.lower().startswith("bearer "):
            token = token[7:].strip()
        client_id = token or request.client.host or "anonymous"

        bucket = self._buckets[client_id]
        # Drop old timestamps
        while bucket and bucket[0] <= now - self.window:
            bucket.popleft()

        if len(bucket) >= self.max_req:
            retry_after = max(0, self.window - (now - bucket[0]))
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "rate limit exceeded"},
                headers={"Retry-After": str(int(retry_after))},
            )

        bucket.append(now)
        return await call_next(request) 