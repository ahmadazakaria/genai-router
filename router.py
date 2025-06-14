"""FastAPI router exposing OpenAI-compatible endpoints.

Currently only ``/v1/chat/completions`` is implemented.  The route inspects
the requested ``model`` field and forwards the request to the appropriate
handler based on the YAML configuration loaded via
``config.backend_loader.resolve_backend``.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from handlers.ollama_handler import handle_chat_completion as ollama_handle, OllamaBackendError
from handlers.http_handler import handle_chat_completion as http_handle, HTTPBackendError
from config.backend_loader import resolve_backend
from schemas.chat import ChatCompletionRequest, ChatCompletionResponse

router = APIRouter()

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(body: ChatCompletionRequest):
    try:
        backend = resolve_backend(body.model)
        backend_type = backend.get("type")

        if backend_type == "ollama":
            result = await ollama_handle(body)
        elif backend_type == "http":
            result = await http_handle(body, base_url=backend["base_url"])
        else:
            return JSONResponse(status_code=400, content={"error": f"Unsupported backend type: {backend_type}"})

    except (OllamaBackendError, HTTPBackendError, ValueError) as e:
        # Forward backend errors as 502 Bad Gateway to the client
        return JSONResponse(status_code=502, content={"error": str(e)})

    # If streaming, result is an async generator (see handler implementation)
    if hasattr(result, "__aiter__"):
        return StreamingResponse(result, media_type="text/event-stream")

    # Validate response with schema before sending back
    validated = ChatCompletionResponse(**result)
    return validated
