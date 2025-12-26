import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.middleware import RequestLoggingMiddleware
from app.api.v1 import router as v1_router
from app.core.settings import get_settings
from app.services.initial_data import create_initial_data
from app.services.parameter import ParameterService
from app.services.satellite import SatelliteService
from app.services.telemetry import TelemetryService
from app.services.unit import UnitService
from app.storage.memory import (
    InMemoryParameterRepository,
    InMemorySatelliteRepository,
    InMemoryTelemetryRepository,
    InMemoryUnitRepository,
)
from app.workers.telemetry_generator import generate_backfill


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

    # Initialize repositories
    satellite_repo = InMemorySatelliteRepository()
    unit_repo = InMemoryUnitRepository()
    parameter_repo = InMemoryParameterRepository()
    telemetry_repo = InMemoryTelemetryRepository()

    # Initialize services
    satellite_service = SatelliteService(satellite_repo)
    unit_service = UnitService(unit_repo, satellite_repo)
    parameter_service = ParameterService(parameter_repo, unit_repo)
    telemetry_service = TelemetryService(
        telemetry_repo,
        parameter_repo,
        unit_repo,
        satellite_repo,
    )

    # Store services in app.state
    app.state.satellite_service = satellite_service
    app.state.unit_service = unit_service
    app.state.parameter_service = parameter_service
    app.state.telemetry_service = telemetry_service

    logger.info("Application starting")
    logger.info("Initializing initial data...")

    # Create deterministic data
    create_initial_data(
        satellite_service,
        unit_service,
        parameter_service,
        telemetry_service,
    )

    logger.info("Initial data initialized")
    logger.info("Health endpoint ready")

    # Start backfill in background (non-blocking)
    async def run_backfill():
        """Run backfill generation in background."""
        await asyncio.to_thread(
            generate_backfill,
            telemetry_service,
            parameter_service,
            settings,
        )

    backfill_task = asyncio.create_task(run_backfill())

    logger.info("Application ready (backfill running in background)")

    yield

    # Cancel backfill if still running
    if not backfill_task.done():
        backfill_task.cancel()
        try:
            await backfill_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Satellite Telemetry API",
    description="""
    REST API for managing satellite telemetry data.

    Features:
    - Satellite and unit management
    - Real-time telemetry data ingestion
    - Parameter monitoring and querying
    - Automatic data generation and backfill
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include v1 API router
app.include_router(v1_router.router, prefix="/v1", tags=["v1"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
