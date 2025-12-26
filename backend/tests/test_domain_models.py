"""Tests for domain models."""

import math
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.domain.models import (
    Parameter,
    ParameterType,
    Satellite,
    SatelliteStatus,
    TelemetryData,
    Unit,
)


class TestSatelliteStatus:
    """Tests for SatelliteStatus enum."""

    def test_active_value(self):
        """Test active status value."""
        assert SatelliteStatus.ACTIVE.value == "active"

    def test_disabled_value(self):
        """Test disabled status value."""
        assert SatelliteStatus.DISABLED.value == "disabled"


class TestParameterType:
    """Tests for ParameterType enum."""

    def test_voltage_value(self):
        """Test voltage type value."""
        assert ParameterType.VOLTAGE.value == "voltage"

    def test_temperature_value(self):
        """Test temperature type value."""
        assert ParameterType.TEMPERATURE.value == "temperature"


class TestSatellite:
    """Tests for Satellite model."""

    def test_create_satellite_with_required_fields(self):
        """Test creating a satellite with only required fields."""
        satellite = Satellite(
            name="Test Satellite",
            launch_date=date(2024, 1, 15),
        )
        assert isinstance(satellite.id, UUID)
        assert satellite.name == "Test Satellite"
        assert satellite.launch_date == date(2024, 1, 15)
        assert satellite.status == SatelliteStatus.ACTIVE
        assert satellite.metadata == {}

    def test_create_satellite_with_all_fields(self):
        """Test creating a satellite with all fields."""
        sat_id = uuid4()
        satellite = Satellite(
            id=sat_id,
            name="Advanced Satellite",
            launch_date=date(2023, 6, 20),
            status=SatelliteStatus.DISABLED,
            metadata={"orbit": "LEO", "mass_kg": 500},
        )
        assert satellite.id == sat_id
        assert satellite.status == SatelliteStatus.DISABLED
        assert satellite.metadata["orbit"] == "LEO"

    def test_empty_name_raises_error(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError, match="must not be empty"):
            Satellite(name="", launch_date=date(2024, 1, 1))

    def test_whitespace_name_raises_error(self):
        """Test that whitespace-only name raises validation error."""
        with pytest.raises(ValueError, match="must not be empty"):
            Satellite(name="   ", launch_date=date(2024, 1, 1))


class TestUnit:
    """Tests for Unit model."""

    def test_create_unit(self):
        """Test creating a unit."""
        sat_id = uuid4()
        unit = Unit(
            satellite_id=sat_id,
            name="Power Subsystem",
            description="Main power distribution unit",
        )
        assert isinstance(unit.id, UUID)
        assert unit.satellite_id == sat_id
        assert unit.name == "Power Subsystem"

    def test_empty_description_raises_error(self):
        """Test that empty description raises validation error."""
        with pytest.raises(ValueError, match="must not be empty"):
            Unit(
                satellite_id=uuid4(),
                name="Test Unit",
                description="",
            )


class TestParameter:
    """Tests for Parameter model."""

    def test_create_parameter(self):
        """Test creating a parameter."""
        unit_id = uuid4()
        param = Parameter(
            unit_id=unit_id,
            name="Battery Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
        )
        assert isinstance(param.id, UUID)
        assert param.unit_id == unit_id
        assert param.name == "Battery Voltage"
        assert param.unit_of_measurement == "V"
        assert param.parameter_type == ParameterType.VOLTAGE
        assert param.is_active is True

    def test_create_inactive_parameter(self):
        """Test creating an inactive parameter."""
        param = Parameter(
            unit_id=uuid4(),
            name="Old Sensor",
            unit_of_measurement="°C",
            parameter_type=ParameterType.TEMPERATURE,
            is_active=False,
        )
        assert param.is_active is False


class TestTelemetryData:
    """Tests for TelemetryData model."""

    def test_create_telemetry_data(self):
        """Test creating telemetry data."""
        param_id = uuid4()
        ts = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        telemetry = TelemetryData(
            parameter_id=param_id,
            timestamp=ts,
            value=12.5,
        )
        assert isinstance(telemetry.id, UUID)
        assert telemetry.parameter_id == param_id
        assert telemetry.timestamp == ts
        assert telemetry.value == 12.5

    def test_naive_timestamp_raises_error(self):
        """Test that naive timestamp raises validation error."""
        with pytest.raises(ValueError, match="timezone-aware"):
            TelemetryData(
                parameter_id=uuid4(),
                timestamp=datetime(2024, 1, 15, 10, 30, 0),
                value=10.0,
            )

    def test_nan_value_raises_error(self):
        """Test that NaN value raises validation error."""
        with pytest.raises(ValueError, match="finite number"):
            TelemetryData(
                parameter_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                value=float("nan"),
            )

    def test_inf_value_raises_error(self):
        """Test that infinite value raises validation error."""
        with pytest.raises(ValueError, match="finite number"):
            TelemetryData(
                parameter_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                value=math.inf,
            )

    def test_negative_inf_value_raises_error(self):
        """Test that negative infinite value raises validation error."""
        with pytest.raises(ValueError, match="finite number"):
            TelemetryData(
                parameter_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                value=-math.inf,
            )
