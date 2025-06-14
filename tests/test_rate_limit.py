import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from config.settings import get_settings
import importlib, sys
if "main" in sys.modules:
    importlib.reload(sys.modules["main"])
else:
    importlib.import_module("main")
from main import app  # new app with rate limit enabled

@pytest_asyncio.fixture
async def client(monkeypatch):
    monkeypatch.setenv("GENAI_RATE_LIMIT", "2/5")
    get_settings.cache_clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_rate_limit(client):
    # First request ok
    r1 = await client.get("/healthz")
    assert r1.status_code == 200
    # Second request ok
    r2 = await client.get("/healthz")
    assert r2.status_code == 200
    # Third request
    r3 = await client.get("/healthz")
    assert r3.status_code in (200, 429)
    if r3.status_code == 200:
        # Fourth must be 429
        r4 = await client.get("/healthz")
        assert r4.status_code == 429
    else:
        r4 = r3
    await asyncio.sleep(5.1)
    r5 = await client.get("/healthz")
    assert r5.status_code == 200 