"""Main FastAPI application entry point with lifespan management and CORS."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.detector import YOLODetector
from app.services.session_manager import SessionManager
from app.routers import health_router, session_router, websocket_router

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("object_detection.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and graceful shutdown."""
    logger.info("Initializing Real-Time Object Detection service...")
    try:
        # Pre-warm default detector model on startup
        detector = YOLODetector.get_instance(settings.DEFAULT_MODEL)
        logger.info(f"Model {detector.model_name} ready on device '{detector.device}'.")
    except Exception as e:
        logger.error(f"Detector failed to initialize on startup: {e}", exc_info=True)

    yield

    logger.info("Shutting down service, releasing camera and session resources...")
    session_manager = SessionManager.get_instance()
    session_manager.cleanup_all()
    logger.info("All resources cleaned up successfully.")


app = FastAPI(
    title="Real-Time Object Detection API",
    description="High-performance FastAPI and YOLOv8 detection backend with WebSocket streaming.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True if origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)},
    )


# Mount routers
app.include_router(health_router)
app.include_router(session_router)
app.include_router(websocket_router)


@app.get("/")
def root():
    return {
        "name": "Real-Time Object Detection API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
    }
