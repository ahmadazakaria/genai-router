"""Generic HTTP backend handler.

This handler forwards the OpenAI-style chat completion request to a remote
server that already speaks the OpenAI protocol (e.g. an internal MCP service).
"""

from __future__ import annotations

from typing import Dict, Any, AsyncGenerator, Union

import httpx

from schemas.chat import ChatCompletionRequest


class HTTPBackendError(Exception):
    """Raised when remote HTTP backend returns an error."""


async def _post_chat(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload)
    if resp.status_code >= 400:
        raise HTTPBackendError(f"HTTP backend error {resp.status_code}: {resp.text}")
    return resp.json()


async def handle_chat_completion(
    request_body: ChatCompletionRequest, *, base_url: str
) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
    """Forward request to HTTP backend.

    Currently only supports non-streaming responses. Streaming could be added
    similarly to the Ollama handler.
    """

    payload = request_body.dict()

    if payload.get("stream"):
        raise HTTPBackendError("Streaming not yet supported for HTTP backend.")

    return await _post_chat(base_url.rstrip("/") + "/v1/chat/completions", payload) 