import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

    yield


app = FastAPI(
    title="Backend API",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
