"""Unit tests for initial data generation."""

from app.domain.models import ParameterType, SatelliteStatus
from app.services.parameter import ParameterService
from app.services.satellite import SatelliteService
from app.services.initial_data import create_initial_data
from app.services.telemetry import TelemetryService
from app.services.unit import UnitService
from app.storage.memory import (
    InMemoryParameterRepository,
    InMemorySatelliteRepository,
    InMemoryTelemetryRepository,
    InMemoryUnitRepository,
)


def test_initial_data_creates_valid_structure():
    """Test that initial data creates valid structural invariants."""
    # Arrange: instantiate repos and services
    satellite_repo = InMemorySatelliteRepository()
    unit_repo = InMemoryUnitRepository()
    parameter_repo = InMemoryParameterRepository()
    telemetry_repo = InMemoryTelemetryRepository()

    satellite_service = SatelliteService(satellite_repo)
    unit_service = UnitService(unit_repo, satellite_repo)
    parameter_service = ParameterService(parameter_repo, unit_repo)
    telemetry_service = TelemetryService(
        telemetry_repo,
        parameter_repo,
        unit_repo,
        satellite_repo,
    )

    # Act: create initial data
    create_initial_data(
        satellite_service,
        unit_service,
        parameter_service,
        telemetry_service,
    )

    # Assert: structural invariants

    # 1. Exactly 1 satellite exists
    satellites = satellite_service.list_all()
    assert len(satellites) == 1, "Expected exactly 1 satellite"
    satellite = satellites[0]

    # 2. Satellite is active
    assert satellite.status == SatelliteStatus.ACTIVE, "Satellite should be active"

    # 3. Exactly 2 units linked to that satellite
    units = unit_service.list_by_satellite(satellite.id)
    assert len(units) == 2, "Expected exactly 2 units"

    # 4. All units belong to the satellite
    for unit in units:
        assert unit.satellite_id == satellite.id, "Unit must belong to the satellite"

    # 5. Between 3 and 5 parameters exist
    all_parameters = []
    for unit in units:
        params = parameter_service.list_by_unit(unit.id)
        all_parameters.extend(params)

    assert 3 <= len(all_parameters) <= 5, "Expected 3-5 parameters total"

    # 6. All parameters are linked to existing units
    unit_ids = {unit.id for unit in units}
    for param in all_parameters:
        assert param.unit_id in unit_ids, "Parameter must belong to an existing unit"

    # 7. All parameters are active
    for param in all_parameters:
        assert param.is_active is True, "All parameters should be active"

    # 8. Coverage: all ParameterType are present at least once
    param_types = {param.parameter_type for param in all_parameters}
    expected_types = {
        ParameterType.VOLTAGE,
        ParameterType.CURRENT,
        ParameterType.POWER,
        ParameterType.TEMPERATURE,
        ParameterType.HUMIDITY,
    }
    assert expected_types.issubset(
        param_types
    ), f"Expected all types {expected_types} to be present, got {param_types}"
