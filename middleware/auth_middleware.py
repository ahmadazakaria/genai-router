from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from config.settings import get_settings


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces simple bearer-token authentication.

    If *GENAI_API_KEYS* environment variable is **unset or empty**, the
    middleware is a no-op (authentication disabled).
    """

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        settings = get_settings()
        allowed_keys = settings.allowed_api_keys

        if not allowed_keys:
            # Auth disabled, skip check.
            return await call_next(request)

        # Extract key from `Authorization: Bearer <token>` or `X-API-Key` header.
        auth_header = request.headers.get("authorization")
        api_key_header = request.headers.get("x-api-key")

        token: str | None = None
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
        elif api_key_header:
            token = api_key_header.strip()

        if token is None or token not in allowed_keys:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"error": "Unauthorized"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request) 