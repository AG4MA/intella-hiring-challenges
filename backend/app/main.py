import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.settings import get_settings


def configure_logging(log_level: str) -> None:
    """Configure standard Python logging."""
    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger = logging.getLogger(__name__)

    # Store settings in app.state
    settings = get_settings()
    app.state.settings = settings

    # Configure logging
    configure_logging(settings.log_level)

    logger.info("Application starting")
    logger.info("Health endpoint ready")

    yield


app = FastAPI(
    title="Backend API",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
