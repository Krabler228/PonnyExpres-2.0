import pytest
from httpx import AsyncClient

from src.app.main import app


@pytest.mark.asyncio
async def test_health_returns_healthy():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "PonnyExpres 2.0"
