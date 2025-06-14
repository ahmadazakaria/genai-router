from __future__ import annotations

import time

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

REQUEST_COUNT = Counter(
    "genai_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "genai_request_latency_seconds",
    "Request latency in seconds",
    ["method", "path"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect Prometheus metrics for each request."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        latency = time.perf_counter() - start

        path = request.url.path
        method = request.method
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(latency)

        return response 