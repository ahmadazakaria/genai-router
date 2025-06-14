"""Application entry point.

Creates the FastAPI app, attaches logging middleware, mounts router, and
registers shutdown handler to cleanly close shared HTTP clients.
"""

from fastapi import FastAPI
from router import router as api_router
from middleware.logging_middleware import RequestLoggingMiddleware
from handlers import ollama_handler

app = FastAPI(title="GenAI Router")

# Structured logging middleware
app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router, prefix="/v1")

# Gracefully close shared HTTP client on shutdown
@app.on_event("shutdown")
async def _shutdown_event():
    await ollama_handler.shutdown()
