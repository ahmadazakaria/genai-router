import time
import uuid
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure root logger with simple JSON-like output
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("genai-router")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID and log structured details."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]):
        request_id = str(uuid.uuid4())
        start = time.time()
        # Make request ID available down the stack
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            status = response.status_code
            error = None
        except Exception as exc:
            status = 500
            error = str(exc)
            raise
        finally:
            duration_ms = (time.time() - start) * 1000
            logger.info(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": round(duration_ms, 2),
                    "error": error,
                }
            )

        # Propagate request ID to clients for debug purposes
        response.headers["X-Request-ID"] = request_id
        return response 