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
from schemas.models import ModelList, ModelInfo
from config import backend_loader

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

@router.get("/models", response_model=ModelList)
async def list_models() -> ModelList:  # noqa: D401
    """Return all configured model names in OpenAI-compatible format.

    The implementation derives the list from ``config/backends.yaml``.  When no
    config file exists, the router is running in *single Ollama* mode, so we
    expose the default ``llama3`` model.
    """

    raw_cfg = backend_loader._load_raw_config()

    models: list[ModelInfo] = []

    if not raw_cfg:
        # No config → single-model Ollama setup.
        models.append(ModelInfo(id="llama3", owned_by="ollama"))
    else:
        routing: dict[str, str] = raw_cfg.get("routing", {})
        backends: dict[str, dict] = raw_cfg.get("backends", {})

        for model_name, backend_key in routing.items():
            backend = backends.get(backend_key, {})
            owned_by = backend.get("type", "backend")
            models.append(ModelInfo(id=model_name, owned_by=owned_by))

    return ModelList(data=models)
