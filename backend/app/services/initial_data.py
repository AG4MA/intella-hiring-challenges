"""Initial data service for deterministic test data."""

from datetime import date, datetime, timezone
from uuid import UUID

from app.domain.models import (
    Parameter,
    ParameterType,
    Satellite,
    SatelliteStatus,
    TelemetryData,
    Unit,
)
from app.services.parameter import ParameterService
from app.services.satellite import SatelliteService
from app.services.telemetry import TelemetryService
from app.services.unit import UnitService


def create_initial_data(
    satellite_service: SatelliteService,
    unit_service: UnitService,
    parameter_service: ParameterService,
    telemetry_service: TelemetryService,
) -> None:
    """Create the initial data with deterministic test data.

    Args:
        satellite_service: The satellite service.
        unit_service: The unit service.
        parameter_service: The parameter service.
        telemetry_service: The telemetry service.
    """
    # Create satellite
    satellite = Satellite(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        name="TestSat-1",
        launch_date=date(2024, 1, 15),
        status=SatelliteStatus.ACTIVE,
        metadata={"orbit": "LEO", "mass_kg": 500, "mission": "Earth observation"},
    )
    satellite_service.create(satellite)

    # Create units
    power_unit = Unit(
        id=UUID("00000000-0000-0000-0000-000000000011"),
        satellite_id=satellite.id,
        name="Power Subsystem",
        description="Main power generation and distribution",
    )
    unit_service.create(power_unit)

    thermal_unit = Unit(
        id=UUID("00000000-0000-0000-0000-000000000012"),
        satellite_id=satellite.id,
        name="Thermal Control",
        description="Temperature regulation system",
    )
    unit_service.create(thermal_unit)

    # Create parameters with full type coverage
    # Power subsystem parameters
    voltage_param = Parameter(
        id=UUID("00000000-0000-0000-0000-000000000101"),
        unit_id=power_unit.id,
        name="Battery Voltage",
        unit_of_measurement="V",
        parameter_type=ParameterType.VOLTAGE,
        is_active=True,
    )
    parameter_service.create(voltage_param)

    current_param = Parameter(
        id=UUID("00000000-0000-0000-0000-000000000102"),
        unit_id=power_unit.id,
        name="Solar Panel Current",
        unit_of_measurement="A",
        parameter_type=ParameterType.CURRENT,
        is_active=True,
    )
    parameter_service.create(current_param)

    power_param = Parameter(
        id=UUID("00000000-0000-0000-0000-000000000103"),
        unit_id=power_unit.id,
        name="Power Output",
        unit_of_measurement="W",
        parameter_type=ParameterType.POWER,
        is_active=True,
    )
    parameter_service.create(power_param)

    # Thermal subsystem parameters
    temp_param = Parameter(
        id=UUID("00000000-0000-0000-0000-000000000201"),
        unit_id=thermal_unit.id,
        name="Internal Temperature",
        unit_of_measurement="°C",
        parameter_type=ParameterType.TEMPERATURE,
        is_active=True,
    )
    parameter_service.create(temp_param)

    humidity_param = Parameter(
        id=UUID("00000000-0000-0000-0000-000000000202"),
        unit_id=thermal_unit.id,
        name="Humidity Level",
        unit_of_measurement="%",
        parameter_type=ParameterType.HUMIDITY,
        is_active=True,
    )
    parameter_service.create(humidity_param)

    # Add some initial telemetry data
    base_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Voltage telemetry
    for i in range(5):
        telemetry = TelemetryData(
            parameter_id=voltage_param.id,
            timestamp=base_time.replace(minute=i * 10),
            value=12.5 + (i * 0.1),  # 12.5V to 12.9V
        )
        telemetry_service.append_point(telemetry)

    # Current telemetry
    for i in range(5):
        telemetry = TelemetryData(
            parameter_id=current_param.id,
            timestamp=base_time.replace(minute=i * 10),
            value=2.0 + (i * 0.05),  # 2.0A to 2.2A
        )
        telemetry_service.append_point(telemetry)

    # Temperature telemetry
    for i in range(5):
        telemetry = TelemetryData(
            parameter_id=temp_param.id,
            timestamp=base_time.replace(minute=i * 10),
            value=20.0 + (i * 0.5),  # 20°C to 22°C
        )
        telemetry_service.append_point(telemetry)
