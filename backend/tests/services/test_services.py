"""Tests for service layer."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain.errors import ConflictError, DomainValidationError, NotFoundError
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
from app.storage.memory import (
    InMemoryParameterRepository,
    InMemorySatelliteRepository,
    InMemoryTelemetryRepository,
    InMemoryUnitRepository,
)


class TestSatelliteService:
    """Tests for SatelliteService."""

    def test_create_satellite(self):
        """Test creating a satellite."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
        )
        result = service.create(satellite)

        assert result.id == satellite.id
        assert result.name == "TestSat"

    def test_get_satellite(self):
        """Test getting a satellite."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
        )
        service.create(satellite)

        result = service.get(satellite.id)
        assert result.id == satellite.id

    def test_get_nonexistent_satellite_raises_not_found(self):
        """Test that getting nonexistent satellite raises NotFoundError."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        with pytest.raises(NotFoundError, match="not found"):
            service.get(uuid4())

    def test_list_all_satellites(self):
        """Test listing all satellites."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        sat1 = Satellite(name="Sat1", launch_date=datetime(2024, 1, 1).date())
        sat2 = Satellite(name="Sat2", launch_date=datetime(2024, 2, 1).date())

        service.create(sat1)
        service.create(sat2)

        results = service.list_all()
        assert len(results) == 2

    def test_update_satellite(self):
        """Test updating a satellite."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        satellite = Satellite(
            name="OldName",
            launch_date=datetime(2024, 1, 1).date(),
        )
        service.create(satellite)

        updated = service.update(satellite.id, name="NewName")
        assert updated.name == "NewName"

    def test_activate_satellite(self):
        """Test activating a satellite."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
            status=SatelliteStatus.DISABLED,
        )
        service.create(satellite)

        result = service.activate(satellite.id)
        assert result.status == SatelliteStatus.ACTIVE

    def test_activate_already_active_raises_conflict(self):
        """Test activating already active satellite raises ConflictError."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
            status=SatelliteStatus.ACTIVE,
        )
        service.create(satellite)

        with pytest.raises(ConflictError, match="already active"):
            service.activate(satellite.id)

    def test_disable_satellite(self):
        """Test disabling a satellite."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
            status=SatelliteStatus.ACTIVE,
        )
        service.create(satellite)

        result = service.disable(satellite.id)
        assert result.status == SatelliteStatus.DISABLED

    def test_disable_already_disabled_raises_conflict(self):
        """Test disabling already disabled satellite raises ConflictError."""
        repo = InMemorySatelliteRepository()
        service = SatelliteService(repo)

        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
            status=SatelliteStatus.DISABLED,
        )
        service.create(satellite)

        with pytest.raises(ConflictError, match="already disabled"):
            service.disable(satellite.id)


class TestUnitService:
    """Tests for UnitService."""

    def test_create_unit(self):
        """Test creating a unit."""
        sat_repo = InMemorySatelliteRepository()
        unit_repo = InMemoryUnitRepository()
        service = UnitService(unit_repo, sat_repo)

        # Create parent satellite
        satellite = Satellite(name="TestSat", launch_date=datetime(2024, 1, 1).date())
        sat_repo.add(satellite)

        # Create unit
        unit = Unit(
            satellite_id=satellite.id,
            name="Power",
            description="Power subsystem",
        )
        result = service.create(unit)

        assert result.id == unit.id

    def test_create_unit_without_satellite_raises_not_found(self):
        """Test creating unit without parent satellite raises NotFoundError."""
        sat_repo = InMemorySatelliteRepository()
        unit_repo = InMemoryUnitRepository()
        service = UnitService(unit_repo, sat_repo)

        unit = Unit(
            satellite_id=uuid4(),
            name="Power",
            description="Power subsystem",
        )

        with pytest.raises(NotFoundError, match="satellite not found"):
            service.create(unit)

    def test_list_by_satellite(self):
        """Test listing units by satellite."""
        sat_repo = InMemorySatelliteRepository()
        unit_repo = InMemoryUnitRepository()
        service = UnitService(unit_repo, sat_repo)

        # Create satellite
        satellite = Satellite(name="TestSat", launch_date=datetime(2024, 1, 1).date())
        sat_repo.add(satellite)

        # Create units
        unit1 = Unit(satellite_id=satellite.id, name="Unit1", description="First")
        unit2 = Unit(satellite_id=satellite.id, name="Unit2", description="Second")

        service.create(unit1)
        service.create(unit2)

        results = service.list_by_satellite(satellite.id)
        assert len(results) == 2

    def test_delete_unit(self):
        """Test deleting a unit."""
        sat_repo = InMemorySatelliteRepository()
        unit_repo = InMemoryUnitRepository()
        service = UnitService(unit_repo, sat_repo)

        # Create satellite and unit
        satellite = Satellite(name="TestSat", launch_date=datetime(2024, 1, 1).date())
        sat_repo.add(satellite)
        unit = Unit(satellite_id=satellite.id, name="Power", description="Power")
        service.create(unit)

        # Delete unit
        service.delete(unit.id)

        with pytest.raises(NotFoundError):
            service.get(unit.id)


class TestParameterService:
    """Tests for ParameterService."""

    def test_create_parameter(self):
        """Test creating a parameter."""
        sat_repo = InMemorySatelliteRepository()
        unit_repo = InMemoryUnitRepository()
        param_repo = InMemoryParameterRepository()
        service = ParameterService(param_repo, unit_repo)

        # Create satellite and unit
        satellite = Satellite(name="TestSat", launch_date=datetime(2024, 1, 1).date())
        sat_repo.add(satellite)
        unit = Unit(satellite_id=satellite.id, name="Power", description="Power")
        unit_repo.add(unit)

        # Create parameter
        param = Parameter(
            unit_id=unit.id,
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
        )
        result = service.create(param)

        assert result.id == param.id

    def test_create_parameter_without_unit_raises_not_found(self):
        """Test creating parameter without parent unit raises NotFoundError."""
        unit_repo = InMemoryUnitRepository()
        param_repo = InMemoryParameterRepository()
        service = ParameterService(param_repo, unit_repo)

        param = Parameter(
            unit_id=uuid4(),
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
        )

        with pytest.raises(NotFoundError, match="unit not found"):
            service.create(param)

    def test_activate_parameter(self):
        """Test activating a parameter."""
        sat_repo = InMemorySatelliteRepository()
        unit_repo = InMemoryUnitRepository()
        param_repo = InMemoryParameterRepository()
        service = ParameterService(param_repo, unit_repo)

        # Setup
        satellite = Satellite(name="TestSat", launch_date=datetime(2024, 1, 1).date())
        sat_repo.add(satellite)
        unit = Unit(satellite_id=satellite.id, name="Power", description="Power")
        unit_repo.add(unit)
        param = Parameter(
            unit_id=unit.id,
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
            is_active=False,
        )
        service.create(param)

        # Activate
        result = service.activate(param.id)
        assert result.is_active is True

    def test_deactivate_parameter(self):
        """Test deactivating a parameter."""
        sat_repo = InMemorySatelliteRepository()
        unit_repo = InMemoryUnitRepository()
        param_repo = InMemoryParameterRepository()
        service = ParameterService(param_repo, unit_repo)

        # Setup
        satellite = Satellite(name="TestSat", launch_date=datetime(2024, 1, 1).date())
        sat_repo.add(satellite)
        unit = Unit(satellite_id=satellite.id, name="Power", description="Power")
        unit_repo.add(unit)
        param = Parameter(
            unit_id=unit.id,
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
            is_active=True,
        )
        service.create(param)

        # Deactivate
        result = service.deactivate(param.id)
        assert result.is_active is False


class TestTelemetryService:
    """Tests for TelemetryService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sat_repo = InMemorySatelliteRepository()
        self.unit_repo = InMemoryUnitRepository()
        self.param_repo = InMemoryParameterRepository()
        self.telemetry_repo = InMemoryTelemetryRepository()

        self.service = TelemetryService(
            self.telemetry_repo,
            self.param_repo,
            self.unit_repo,
            self.sat_repo,
        )

        # Create test data
        self.satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
            status=SatelliteStatus.ACTIVE,
        )
        self.sat_repo.add(self.satellite)

        self.unit = Unit(
            satellite_id=self.satellite.id,
            name="Power",
            description="Power subsystem",
        )
        self.unit_repo.add(self.unit)

        self.parameter = Parameter(
            unit_id=self.unit.id,
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
            is_active=True,
        )
        self.param_repo.add(self.parameter)

    def test_append_point(self):
        """Test appending a telemetry point."""
        telemetry = TelemetryData(
            parameter_id=self.parameter.id,
            timestamp=datetime.now(timezone.utc),
            value=12.5,
        )

        result = self.service.append_point(telemetry)
        assert result.id == telemetry.id

    def test_append_point_with_inactive_parameter_raises_validation_error(self):
        """Test appending to inactive parameter raises DomainValidationError."""
        self.parameter.is_active = False

        telemetry = TelemetryData(
            parameter_id=self.parameter.id,
            timestamp=datetime.now(timezone.utc),
            value=12.5,
        )

        with pytest.raises(DomainValidationError, match="inactive parameter"):
            self.service.append_point(telemetry)

    def test_append_point_with_inactive_satellite_raises_validation_error(self):
        """Test appending with inactive satellite raises DomainValidationError."""
        self.satellite.status = SatelliteStatus.DISABLED

        telemetry = TelemetryData(
            parameter_id=self.parameter.id,
            timestamp=datetime.now(timezone.utc),
            value=12.5,
        )

        with pytest.raises(DomainValidationError, match="inactive satellite"):
            self.service.append_point(telemetry)

    def test_validate_temperature_below_absolute_zero(self):
        """Test temperature validation rejects values below absolute zero."""
        self.parameter.parameter_type = ParameterType.TEMPERATURE

        telemetry = TelemetryData(
            parameter_id=self.parameter.id,
            timestamp=datetime.now(timezone.utc),
            value=-300.0,  # Below absolute zero
        )

        with pytest.raises(DomainValidationError, match="absolute zero"):
            self.service.append_point(telemetry)

    def test_validate_negative_current(self):
        """Test current validation rejects negative values."""
        self.parameter.parameter_type = ParameterType.CURRENT

        telemetry = TelemetryData(
            parameter_id=self.parameter.id,
            timestamp=datetime.now(timezone.utc),
            value=-5.0,
        )

        with pytest.raises(DomainValidationError, match="non-negative"):
            self.service.append_point(telemetry)

    def test_validate_humidity_out_of_range(self):
        """Test humidity validation rejects values outside 0-100."""
        self.parameter.parameter_type = ParameterType.HUMIDITY

        telemetry = TelemetryData(
            parameter_id=self.parameter.id,
            timestamp=datetime.now(timezone.utc),
            value=150.0,
        )

        with pytest.raises(DomainValidationError, match="0 and 100"):
            self.service.append_point(telemetry)

    def test_query_telemetry(self):
        """Test querying telemetry data."""
        # Add some telemetry
        for i in range(5):
            telemetry = TelemetryData(
                parameter_id=self.parameter.id,
                timestamp=datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc),
                value=float(i),
            )
            self.service.append_point(telemetry)

        # Query
        results = self.service.query(self.parameter.id)
        assert len(results) == 5

    def test_query_with_limit(self):
        """Test querying telemetry with limit."""
        # Add some telemetry
        for i in range(10):
            telemetry = TelemetryData(
                parameter_id=self.parameter.id,
                timestamp=datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc),
                value=float(i),
            )
            self.service.append_point(telemetry)

        # Query with limit
        results = self.service.query(self.parameter.id, limit=3)
        assert len(results) == 3
        assert results[0].value == 7.0  # Most recent 3

    def test_query_with_time_range(self):
        """Test querying telemetry with time range."""
        # Add some telemetry
        for i in range(10):
            telemetry = TelemetryData(
                parameter_id=self.parameter.id,
                timestamp=datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc),
                value=float(i),
            )
            self.service.append_point(telemetry)

        # Query with time range
        start = datetime(2024, 1, 1, 12, 3, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 6, 0, tzinfo=timezone.utc)
        results = self.service.query(
            self.parameter.id,
            start_time=start,
            end_time=end,
        )

        assert len(results) == 4  # Minutes 3, 4, 5, 6
        assert results[0].value == 3.0

    def test_query_nonexistent_parameter_raises_not_found(self):
        """Test querying nonexistent parameter raises NotFoundError."""
        with pytest.raises(NotFoundError, match="not found"):
            self.service.query(uuid4())
