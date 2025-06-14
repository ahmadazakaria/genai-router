"""Application entry point.

Creates the FastAPI app, attaches logging middleware, mounts router, and
registers shutdown handler to cleanly close shared HTTP clients.
"""

from fastapi import FastAPI
from router import router as api_router
from middleware.logging_middleware import RequestLoggingMiddleware
from handlers import ollama_handler
from middleware.auth_middleware import APIKeyAuthMiddleware
from fastapi.responses import Response

# Prometheus (optional dev dependency)
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from middleware.metrics_middleware import MetricsMiddleware

    _PROM_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    _PROM_AVAILABLE = False

app = FastAPI(title="GenAI Router")

# API key auth middleware (no-op when GENAI_API_KEYS empty)
app.add_middleware(APIKeyAuthMiddleware)

# Structured logging middleware
app.add_middleware(RequestLoggingMiddleware)

if _PROM_AVAILABLE:
    app.add_middleware(MetricsMiddleware)

app.include_router(api_router, prefix="/v1")

# Gracefully close shared HTTP client on shutdown
@app.on_event("shutdown")
async def _shutdown_event():
    await ollama_handler.shutdown()

# Expose Prometheus metrics
if _PROM_AVAILABLE:
    @app.get("/metrics")
    async def metrics() -> Response:  # noqa: D401
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
else:
    @app.get("/metrics")
    async def metrics_unavailable() -> Response:  # noqa: D401
        return Response("Prometheus metrics unavailable", status_code=503)

# Simple health probe
@app.get("/healthz")
async def healthz() -> dict[str, str]:  # noqa: D401
    return {"status": "ok"}
