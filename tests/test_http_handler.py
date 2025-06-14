import asyncio
from types import SimpleNamespace
from typing import AsyncGenerator

import httpx
import pytest

from handlers import http_handler


class DummyStreamContext:
    def __init__(self, lines):
        self._lines = lines
        self.status_code = 200
        self.headers = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def aiter_lines(self):
        for ln in self._lines:
            yield ln


@pytest.mark.asyncio
async def test_http_handler_non_stream(monkeypatch):
    """handle_chat_completion should return dict when stream is False."""

    response_payload = {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "model": "dummy",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "hi"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }

    async def fake_post(self, url, json):  # noqa: D401  pylint: disable=unused-argument
        return httpx.Response(status_code=200, json=response_payload)

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

    body = http_handler.ChatCompletionRequest.model_validate(  # type: ignore[attr-defined]
        {"model": "dummy", "messages": [{"role": "user", "content": "hi"}]}
    )

    result = await http_handler.handle_chat_completion(body, base_url="http://fake")
    assert isinstance(result, dict)
    assert result["choices"][0]["message"]["content"] == "hi"


@pytest.mark.asyncio
async def test_http_handler_stream(monkeypatch):
    """handle_chat_completion should return async generator when stream flag true."""

    lines = ["data: {\"delta\":\"h\"}", "data: {\"delta\":\"i\"}"]

    def fake_stream(self, method, url, json):  # noqa: D401  pylint: disable=unused-argument
        return DummyStreamContext(lines)

    monkeypatch.setattr(httpx.AsyncClient, "stream", fake_stream, raising=True)

    body = http_handler.ChatCompletionRequest.model_validate(  # type: ignore[attr-defined]
        {
            "model": "dummy",
            "stream": True,
            "messages": [{"role": "user", "content": "hi"}],
        }
    )

    gen = await http_handler.handle_chat_completion(body, base_url="http://fake")
    assert hasattr(gen, "__aiter__")
    collected = []
    async for chunk in gen:  # type: ignore[attr-defined]
        collected.append(chunk.strip())
    assert collected == [ln + "\n\n".strip() for ln in lines] 