"""Configuration management using Pydantic Settings."""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS settings
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # Model settings
    DEFAULT_MODEL: str = "yolov8n.pt"
    ALLOWED_MODELS: Union[str, List[str]] = "yolov8n.pt,yolov8s.pt,yolov8m.pt"
    MODELS_DIR: str = "models"
    INFERENCE_DEVICE: str = "cpu"

    # Default detection thresholds
    DEFAULT_CONFIDENCE_THRESHOLD: float = Field(default=0.45, ge=0.01, le=1.0)
    DEFAULT_IOU_THRESHOLD: float = Field(default=0.45, ge=0.01, le=1.0)

    # Frame processing limits
    MAX_FRAME_SIZE_MB: float = Field(default=5.0, gt=0.0)
    FRAME_QUEUE_MAX_SIZE: int = Field(default=1, ge=1)

    # Safety limits
    MAX_STREAM_FPS: int = Field(default=30, ge=1, le=60)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("ALLOWED_MODELS", mode="after")
    @classmethod
    def parse_allowed_models(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            return [m.strip() for m in value.split(",") if m.strip()]
        return value

    def is_model_allowed(self, model_name: str) -> bool:
        """Check whether a requested model name is in the allowed whitelist."""
        allowed = self.ALLOWED_MODELS if isinstance(self.ALLOWED_MODELS, list) else []
        return model_name in allowed


settings = Settings()
