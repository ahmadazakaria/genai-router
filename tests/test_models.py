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
async def test_list_models(client, monkeypatch):
    monkeypatch.delenv("GENAI_API_KEYS", raising=False)
    monkeypatch.delenv("GENAI_RATE_LIMIT", raising=False)
    get_settings.cache_clear()
    import importlib, sys
    importlib.reload(sys.modules["main"])

    resp = await client.get("/v1/models")
    assert resp.status_code == 200

    payload = resp.json()
    assert payload["object"] == "list"
    assert isinstance(payload["data"], list)

    model_ids = {model["id"] for model in payload["data"]}
    # At minimum expect llama3 present (from sample config or default)
    assert "llama3" in model_ids 