"""Generic HTTP backend handler.

This handler forwards the OpenAI-style chat completion request to a remote
server that already speaks the OpenAI protocol (e.g. an internal MCP service).
"""

from __future__ import annotations

from typing import Dict, Any, AsyncGenerator, Union
import json

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


async def _stream_chat(url: str, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Stream chat completion chunks from an OpenAI-compatible HTTP backend."""

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload) as resp:
            if resp.status_code >= 400:
                raise HTTPBackendError(
                    f"HTTP backend error {resp.status_code}: {await resp.aread()}"
                )

            async for line in resp.aiter_lines():
                if not line:
                    continue
                # Ensure SSE format (prefix with data: )
                if not line.startswith("data:"):
                    line = f"data: {line}"
                yield line + "\n\n"


async def handle_chat_completion(
    request_body: ChatCompletionRequest, *, base_url: str
) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
    """Forward request to HTTP backend.

    Currently only supports non-streaming responses. Streaming could be added
    similarly to the Ollama handler.
    """

    payload = request_body.model_dump()

    url = base_url.rstrip("/") + "/v1/chat/completions"

    if payload.get("stream"):
        return _stream_chat(url, payload)

    resp = await _post_chat(url, payload)
    # Ensure OpenAI schema (backend assumed compatible)
    return resp 