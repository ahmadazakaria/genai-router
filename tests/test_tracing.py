import importlib, os, sys

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

pytest.importorskip("opentelemetry")
from opentelemetry import trace  # type: ignore


@pytest_asyncio.fixture
async def client(monkeypatch):
    monkeypatch.setenv("GENAI_OTEL_ENDPOINT", "")  # console exporter
    from config.settings import get_settings
    get_settings.cache_clear()

    if "main" in sys.modules:
        importlib.reload(sys.modules["main"])
    else:
        importlib.import_module("main")
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_tracer_provider_initialised(client):
    resp = await client.get("/healthz")
    assert resp.status_code == 200

    provider = trace.get_tracer_provider()
    # SDK provider class name contains 'TracerProvider'
    assert provider.__class__.__name__.endswith("TracerProvider") 