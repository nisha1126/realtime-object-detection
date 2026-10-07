"""Unit tests for configuration and settings."""

import pytest
from app.config import Settings


def test_default_settings():
    settings = Settings()
    assert settings.PORT == 8000
    assert settings.DEFAULT_MODEL == "yolov8n.pt"
    assert settings.is_model_allowed("yolov8n.pt") is True
    assert settings.is_model_allowed("malicious_model_eval.pt") is False


def test_cors_origins_parsing():
    settings = Settings(CORS_ORIGINS="http://localhost:3000, http://test.com")
    assert "http://localhost:3000" in settings.CORS_ORIGINS
    assert "http://test.com" in settings.CORS_ORIGINS


def test_allowed_models_parsing():
    settings = Settings(ALLOWED_MODELS="yolov8n.pt,yolov8s.pt")
    assert settings.is_model_allowed("yolov8n.pt") is True
    assert settings.is_model_allowed("yolov8s.pt") is True
    assert settings.is_model_allowed("custom_unapproved.pt") is False
