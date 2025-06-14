import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app
from config.settings import get_settings


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_auth_missing_key(monkeypatch, client):
    monkeypatch.setenv("GENAI_API_KEYS", "secret123")
    get_settings.cache_clear()
    import importlib, sys
    importlib.reload(sys.modules["main"])

    resp = await client.get("/v1/models")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_valid_key(monkeypatch, client):
    monkeypatch.setenv("GENAI_API_KEYS", "secret123")
    get_settings.cache_clear()
    import importlib, sys
    importlib.reload(sys.modules["main"])

    headers = {"Authorization": "Bearer secret123"}
    resp = await client.get("/v1/models", headers=headers)
    assert resp.status_code == 200 