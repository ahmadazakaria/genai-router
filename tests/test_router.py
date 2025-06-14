import json

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from config import backend_loader
from handlers import ollama_handler, http_handler
from main import app
from config.settings import get_settings


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def clear_cache():
    # Ensure backend loader cache cleared before each test
    backend_loader._load_raw_config.cache_clear()
    yield
    backend_loader._load_raw_config.cache_clear()


async def _dummy_response(request_body):
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "model": request_body.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "dummy"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }


@pytest.mark.asyncio
async def test_chat_completion_ollama(monkeypatch, client):
    # Mock resolution to ollama backend
    monkeypatch.setattr(backend_loader, "resolve_backend", lambda model: {"type": "ollama"})
    monkeypatch.setattr(ollama_handler, "handle_chat_completion", _dummy_response)
    monkeypatch.delenv("GENAI_API_KEYS", raising=False)
    get_settings.cache_clear()

    payload = {"model": "llama3", "messages": [{"role": "user", "content": "hi"}]}
    resp = await client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["model"] == "llama3"


@pytest.mark.asyncio
async def test_chat_completion_http(monkeypatch, client):
    monkeypatch.setattr(backend_loader, "resolve_backend", lambda model: {"type": "http", "base_url": "http://remote"})
    import router as router_module
    monkeypatch.setattr(router_module, "http_handle", lambda body, base_url: _dummy_response(body))
    monkeypatch.delenv("GENAI_API_KEYS", raising=False)
    get_settings.cache_clear()

    payload = {"model": "company-gpt", "messages": [{"role": "user", "content": "hello"}]}
    resp = await client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["model"] == "company-gpt" 