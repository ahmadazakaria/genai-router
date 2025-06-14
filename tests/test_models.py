import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_models(client):
    resp = await client.get("/v1/models")
    assert resp.status_code == 200

    payload = resp.json()
    assert payload["object"] == "list"
    assert isinstance(payload["data"], list)

    model_ids = {model["id"] for model in payload["data"]}
    # At minimum expect llama3 present (from sample config or default)
    assert "llama3" in model_ids 