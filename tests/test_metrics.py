import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from config.settings import get_settings
import importlib

from main import app

PROM_AVAILABLE = importlib.util.find_spec("prometheus_client") is not None


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_healthz(client, monkeypatch):
    monkeypatch.delenv("GENAI_API_KEYS", raising=False)
    get_settings.cache_clear()
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.skipif(not PROM_AVAILABLE, reason="prometheus_client not installed")
@pytest.mark.asyncio
async def test_metrics(client, monkeypatch):
    monkeypatch.delenv("GENAI_API_KEYS", raising=False)
    get_settings.cache_clear()
    # Make one request to increment metrics
    await client.get("/healthz")
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert "genai_requests_total" in resp.text 