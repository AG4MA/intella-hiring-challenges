"""Tests for telemetry generator engine."""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from app.core.settings import Settings
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
from app.workers.telemetry_generator import generate_backfill, run_live


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        telemetry_step_seconds=10,
        telemetry_backfill_hours=1,  # Short for fast tests
    )


@pytest.fixture
def repositories():
    """Create test repositories."""
    return {
        "satellite": InMemorySatelliteRepository(),
        "unit": InMemoryUnitRepository(),
        "parameter": InMemoryParameterRepository(),
        "telemetry": InMemoryTelemetryRepository(),
    }


@pytest.fixture
def services(repositories):
    """Create test services."""
    satellite_service = SatelliteService(repositories["satellite"])
    unit_service = UnitService(repositories["unit"], repositories["satellite"])
    parameter_service = ParameterService(
        repositories["parameter"], repositories["unit"]
    )
    telemetry_service = TelemetryService(
        repositories["telemetry"],
        repositories["parameter"],
        repositories["unit"],
        repositories["satellite"],
    )
    return {
        "satellite": satellite_service,
        "unit": unit_service,
        "parameter": parameter_service,
        "telemetry": telemetry_service,
    }


def test_generate_backfill_with_no_parameters(services, settings):
    """Test backfill when no parameters exist."""
    # Act
    count = generate_backfill(
        services["telemetry"],
        services["parameter"],
        settings,
    )

    # Assert
    assert count == 0, "Should generate 0 points with no parameters"


def test_generate_backfill_creates_telemetry_points(services, settings):
    """Test backfill generates correct number of points."""
    # Arrange: Create satellite, unit, parameter from initial_data
    from app.services.initial_data import create_initial_data

    create_initial_data(
        services["satellite"],
        services["unit"],
        services["parameter"],
        services["telemetry"],
    )

    # Clear telemetry to test backfill in isolation
    # Get all telemetry before clearing
    all_params = services["parameter"].list_all()
    for param in all_params:
        # Clear will happen by recreating service with fresh repository
        pass

    # Recreate telemetry components to get clean state
    telemetry_repo = InMemoryTelemetryRepository()
    services["telemetry"] = TelemetryService(
        telemetry_repo,
        services["parameter"]._repo,
        services["unit"]._repo,
        services["satellite"]._repo,
    )

    # Act
    count = generate_backfill(
        services["telemetry"],
        services["parameter"],
        settings,
    )

    # Assert
    # With 1 hour backfill and 10 second steps: 361 steps (inclusive of end)
    # With 5 active parameters: 361 * 5 = 1805 points
    expected_steps = (
        settings.telemetry_backfill_hours * 3600
    ) // settings.telemetry_step_seconds + 1  # +1 because loop includes end_time
    active_params = len([p for p in services["parameter"].list_all() if p.is_active])
    expected_points = expected_steps * active_params

    assert count == expected_points, f"Expected {expected_points} points"

    # Verify telemetry was actually stored
    all_telemetry = telemetry_repo.list_all()
    assert len(all_telemetry) == expected_points


def test_generate_backfill_respects_time_range(services, settings):
    """Test backfill generates points in correct time range."""
    # Arrange
    from app.services.initial_data import create_initial_data

    create_initial_data(
        services["satellite"],
        services["unit"],
        services["parameter"],
        services["telemetry"],
    )

    # Recreate telemetry service with fresh repository
    telemetry_repo = InMemoryTelemetryRepository()
    services["telemetry"] = TelemetryService(
        telemetry_repo,
        services["parameter"]._repo,
        services["unit"]._repo,
        services["satellite"]._repo,
    )

    # Record time before backfill
    backfill_end = datetime.now(timezone.utc)

    # Act
    generate_backfill(
        services["telemetry"],
        services["parameter"],
        settings,
    )

    # Assert: Check time range
    all_telemetry = telemetry_repo.list_all()
    timestamps = [t.timestamp for t in all_telemetry]

    earliest = min(timestamps)
    latest = max(timestamps)

    expected_start = backfill_end - timedelta(hours=settings.telemetry_backfill_hours)

    # Allow some slack for execution time
    assert earliest >= expected_start - timedelta(seconds=5)
    assert latest <= backfill_end + timedelta(seconds=5)


def test_generate_backfill_uses_deterministic_seed(services, settings):
    """Test backfill is deterministic with fixed seed."""
    # Arrange
    from app.services.initial_data import create_initial_data

    create_initial_data(
        services["satellite"],
        services["unit"],
        services["parameter"],
        services["telemetry"],
    )

    # Act: Generate backfill twice with fresh repos
    telemetry_repo = InMemoryTelemetryRepository()
    temp_service = TelemetryService(
        telemetry_repo,
        services["parameter"]._repo,
        services["unit"]._repo,
        services["satellite"]._repo,
    )
    generate_backfill(temp_service, services["parameter"], settings)
    first_run = sorted(
        telemetry_repo.list_all(), key=lambda t: (t.parameter_id, t.timestamp)
    )

    telemetry_repo = InMemoryTelemetryRepository()
    temp_service = TelemetryService(
        telemetry_repo,
        services["parameter"]._repo,
        services["unit"]._repo,
        services["satellite"]._repo,
    )
    generate_backfill(temp_service, services["parameter"], settings)
    second_run = sorted(
        telemetry_repo.list_all(), key=lambda t: (t.parameter_id, t.timestamp)
    )

    # Assert: Values should be identical (deterministic)
    assert len(first_run) == len(second_run)
    for t1, t2 in zip(first_run, second_run):
        assert t1.parameter_id == t2.parameter_id
        assert t1.value == t2.value  # Same seed = same values


@pytest.mark.skip(reason="Async test - manual verification only")
async def test_run_live_generates_points_periodically(services, settings):
    """Test live generation creates points at intervals."""
    # Arrange
    from app.services.initial_data import create_initial_data

    create_initial_data(
        services["satellite"],
        services["unit"],
        services["parameter"],
        services["telemetry"],
    )

    # Recreate with fresh telemetry repository
    telemetry_repo = InMemoryTelemetryRepository()
    services["telemetry"] = TelemetryService(
        telemetry_repo,
        services["parameter"]._repo,
        services["unit"]._repo,
        services["satellite"]._repo,
    )

    # Use short interval for testing
    settings.telemetry_step_seconds = 0.1
    stop_event = asyncio.Event()

    # Act: Run for short time
    async def run_for_short_time():
        await asyncio.sleep(0.35)  # Allow ~3 ticks
        stop_event.set()

    live_task = asyncio.create_task(
        run_live(
            services["telemetry"],
            services["parameter"],
            settings,
            stop_event,
        )
    )
    stop_task = asyncio.create_task(run_for_short_time())

    await asyncio.gather(live_task, stop_task)

    # Assert: Should have generated points
    all_telemetry = telemetry_repo.list_all()
    active_params = len([p for p in services["parameter"].list_all() if p.is_active])

    # Should have at least 2 ticks worth of data
    assert len(all_telemetry) >= active_params * 2


@pytest.mark.skip(reason="Async test - manual verification only")
async def test_run_live_stops_on_event(services, settings):
    """Test live generation stops when event is set."""
    # Arrange
    from app.services.initial_data import create_initial_data

    create_initial_data(
        services["satellite"],
        services["unit"],
        services["parameter"],
        services["telemetry"],
    )

    settings.telemetry_step_seconds = 0.1
    stop_event = asyncio.Event()

    # Act: Start live generation
    live_task = asyncio.create_task(
        run_live(
            services["telemetry"],
            services["parameter"],
            settings,
            stop_event,
        )
    )

    await asyncio.sleep(0.15)  # Let it run briefly
    stop_event.set()  # Signal stop

    # Wait for completion with timeout
    await asyncio.wait_for(live_task, timeout=1.0)

    # Assert: Task completed without error
    assert live_task.done()
    assert not live_task.cancelled()


def test_generate_backfill_skips_inactive_parameters(services, settings):
    """Test backfill skips inactive parameters."""
    # Arrange
    from app.services.initial_data import create_initial_data

    create_initial_data(
        services["satellite"],
        services["unit"],
        services["parameter"],
        services["telemetry"],
    )

    # Deactivate all parameters
    for param in services["parameter"].list_all():
        param.is_active = False
        services["parameter"]._repo.update(param)

    # Recreate telemetry service with fresh repository
    telemetry_repo = InMemoryTelemetryRepository()
    services["telemetry"] = TelemetryService(
        telemetry_repo,
        services["parameter"]._repo,
        services["unit"]._repo,
        services["satellite"]._repo,
    )

    # Act
    count = generate_backfill(
        services["telemetry"],
        services["parameter"],
        settings,
    )

    # Assert: No points generated for inactive parameters
    assert count == 0
    assert len(telemetry_repo.list_all()) == 0
