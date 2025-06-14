"""Ollama backend adapter.

This module provides an async handler that forwards OpenAI-compatible
chat-completion requests to a local or remote **Ollama** server.  It exposes:

* `handle_chat_completion` – the public coroutine used by the FastAPI router.
* `shutdown` – cleans up the shared `httpx.AsyncClient` during application
  shutdown.

It adheres to the project rules:
• Async-only I/O using ``httpx``.
• No blocking operations.
• Fully documented for Sphinx (Google-style docstrings).
"""

from typing import Dict, Any, AsyncGenerator, Union
import json

import httpx

from config.settings import get_settings
from schemas.chat import ChatCompletionRequest

# Re-use a single AsyncClient across requests (created lazily).

_client: httpx.AsyncClient | None = None


async def _get_client() -> httpx.AsyncClient:
    """Return a shared httpx.AsyncClient instance."""

    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=60.0)
    return _client


class OllamaBackendError(Exception):
    """Raised when Ollama backend returns an unexpected error."""


async def _post_ollama_chat(payload: Dict[str, Any]) -> Dict[str, Any]:
    settings = get_settings()
    url = settings.ollama_base_url.rstrip("/") + "/api/chat"

    # Ensure we explicitly ask for non-streaming, but Ollama may still stream.
    payload.setdefault("stream", False)

    client = await _get_client()

    if payload.get("stream"):
        # We expect a streamed response; return generator to caller
        return await _stream_ollama_chat(payload)

    # Non-streaming request – first try a simple POST; Ollama might still stream
    resp = await client.post(url, json=payload)
    if resp.status_code >= 400:
        raise OllamaBackendError(
            f"Ollama backend error {resp.status_code}: {resp.text}"  # text reads entire body
        )

    content_type = resp.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        return _ollama_to_openai(resp.json())

    # Fallback: Ollama ignored stream=false and is streaming; aggregate chunks
    last_msg: Dict[str, Any] | None = None
    async for line in resp.aiter_lines():
        if not line:
            continue
        try:
            last_msg = json.loads(line)
        except json.JSONDecodeError:
            continue
    if last_msg is None:
        raise OllamaBackendError("Ollama returned empty streaming response")

    # Convert Ollama final message to OpenAI chat completion response shape
    return _ollama_to_openai(last_msg)


async def _stream_ollama_chat(payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Stream completion chunks from Ollama and yield as SSE lines."""

    settings = get_settings()
    url = settings.ollama_base_url.rstrip("/") + "/api/chat"

    client = await _get_client()
    async with client.stream("POST", url, json=payload) as resp:
        if resp.status_code >= 400:
            text = await resp.aread()
            raise OllamaBackendError(f"Ollama backend error {resp.status_code}: {text}")

        async for line in resp.aiter_lines():
            # Ollama already sends plain JSON lines. Convert to SSE format.
            if not line:
                continue
            yield f"data: {line}\n\n"


async def handle_chat_completion(request_body: ChatCompletionRequest) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
    """Forward a ChatCompletionRequest to the Ollama HTTP server and return the raw JSON."""

    payload = request_body.dict()

    if payload.get("stream"):
        # Return an async generator producing SSE text lines
        return _stream_ollama_chat(payload)

    return await _post_ollama_chat(payload)


async def shutdown() -> None:
    """Close the shared HTTP client (called on FastAPI shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ollama_to_openai(msg: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Ollama's final chunk into an OpenAI-compatible response."""

    message = msg.get("message", {})
    return {
        "id": msg.get("id", "chatcmpl-ollama"),
        "object": "chat.completion",
        "model": msg.get("model"),
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": msg.get("done_reason", "stop"),
            }
        ],
        "usage": msg.get(
            "usage",
            {
                "prompt_tokens": msg.get("prompt_eval_count", 0),
                "completion_tokens": msg.get("eval_count", 0),
                "total_tokens": msg.get("eval_count", 0) + msg.get("prompt_eval_count", 0),
            },
        ),
    }
