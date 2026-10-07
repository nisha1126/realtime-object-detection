"""Integration tests for FastAPI endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert "model_loaded" in data
        assert "current_model" in data
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_config_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "default_model" in data
        assert "allowed_models" in data
        assert "default_confidence" in data
        assert "default_iou" in data


@pytest.mark.asyncio
async def test_session_lifecycle_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Start session
        start_payload = {
            "source_type": "client",
            "confidence_threshold": 0.5,
            "iou_threshold": 0.45,
        }
        res_start = await ac.post("/api/session/start", json=start_payload)
        assert res_start.status_code == 200
        session_data = res_start.json()
        session_id = session_data["session_id"]
        assert session_data["state"] == "running"

        # Get status
        res_status = await ac.get(f"/api/session/status?session_id={session_id}")
        assert res_status.status_code == 200
        assert res_status.json()["state"] == "running"

        # Pause session
        res_pause = await ac.post(f"/api/session/pause?session_id={session_id}")
        assert res_pause.status_code == 200
        assert res_pause.json()["state"] == "paused"

        # Resume session
        res_resume = await ac.post(f"/api/session/resume?session_id={session_id}")
        assert res_resume.status_code == 200
        assert res_resume.json()["state"] == "running"

        # Stop session
        res_stop = await ac.post(f"/api/session/stop?session_id={session_id}")
        assert res_stop.status_code == 200
        assert res_stop.json()["state"] == "stopped"


@pytest.mark.asyncio
async def test_invalid_stream_url_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "source_type": "stream",
            "stream_url": "ftp://malicious-host/stream",
        }
        res = await ac.post("/api/session/start", json=payload)
        assert res.status_code == 422  # Validation error
