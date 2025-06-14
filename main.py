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
from middleware.ratelimit_middleware import RateLimitMiddleware
from typing import Any
from contextlib import asynccontextmanager

# Prometheus (optional dev dependency)
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from middleware.metrics_middleware import MetricsMiddleware

    _PROM_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    _PROM_AVAILABLE = False

# OpenTelemetry (optional)
try:
    import os
    from opentelemetry import trace  # type: ignore
    from opentelemetry.sdk.resources import Resource  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter  # type: ignore
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore

    _OTEL_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    _OTEL_AVAILABLE = False

@asynccontextmanager
async def lifespan(app):
    yield
    await ollama_handler.shutdown()

app = FastAPI(title="GenAI Router", lifespan=lifespan)

# API key auth middleware (no-op when GENAI_API_KEYS empty)
app.add_middleware(APIKeyAuthMiddleware)

# Structured logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Rate limit middleware
app.add_middleware(RateLimitMiddleware)

if _PROM_AVAILABLE:
    app.add_middleware(MetricsMiddleware)

app.include_router(api_router, prefix="/v1")

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

# --------------------
# OpenTelemetry setup
# --------------------

if _OTEL_AVAILABLE and not getattr(app.state, "otel_instrumented", False):
    endpoint = os.getenv("GENAI_OTEL_ENDPOINT")
    service_name = os.getenv("GENAI_OTEL_SERVICE_NAME", "genai-router")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if endpoint:
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor().instrument_app(app, tracer_provider=provider)
    HTTPXClientInstrumentor().instrument(tracer_provider=provider)

    app.state.otel_instrumented = True
