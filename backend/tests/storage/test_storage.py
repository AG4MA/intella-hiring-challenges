"""Tests for in-memory storage repositories."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.domain.errors import ConflictError
from app.domain.models import (
    Parameter,
    ParameterType,
    Satellite,
    TelemetryData,
    Unit,
)
from app.storage.memory import (
    InMemoryParameterRepository,
    InMemorySatelliteRepository,
    InMemoryTelemetryRepository,
    InMemoryUnitRepository,
)


class TestInMemorySatelliteRepository:
    """Tests for InMemorySatelliteRepository."""

    def test_add_satellite(self):
        """Test adding a satellite."""
        repo = InMemorySatelliteRepository()
        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
        )

        result = repo.add(satellite)

        assert result.id == satellite.id
        assert repo.get(satellite.id) == satellite

    def test_add_duplicate_satellite_raises_conflict(self):
        """Test that adding duplicate satellite raises ConflictError."""
        repo = InMemorySatelliteRepository()
        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
        )
        repo.add(satellite)

        with pytest.raises(ConflictError, match="already exists"):
            repo.add(satellite)

    def test_get_nonexistent_satellite(self):
        """Test getting a non-existent satellite returns None."""
        repo = InMemorySatelliteRepository()
        assert repo.get(uuid4()) is None

    def test_list_all_satellites(self):
        """Test listing all satellites."""
        repo = InMemorySatelliteRepository()
        sat1 = Satellite(name="Sat1", launch_date=datetime(2024, 1, 1).date())
        sat2 = Satellite(name="Sat2", launch_date=datetime(2024, 2, 1).date())

        repo.add(sat1)
        repo.add(sat2)

        satellites = repo.list_all()
        assert len(satellites) == 2
        assert sat1 in satellites
        assert sat2 in satellites

    def test_delete_satellite(self):
        """Test deleting a satellite."""
        repo = InMemorySatelliteRepository()
        satellite = Satellite(
            name="TestSat",
            launch_date=datetime(2024, 1, 1).date(),
        )
        repo.add(satellite)

        assert repo.delete(satellite.id) is True
        assert repo.get(satellite.id) is None

    def test_delete_nonexistent_satellite(self):
        """Test deleting a non-existent satellite returns False."""
        repo = InMemorySatelliteRepository()
        assert repo.delete(uuid4()) is False


class TestInMemoryUnitRepository:
    """Tests for InMemoryUnitRepository."""

    def test_add_unit(self):
        """Test adding a unit."""
        repo = InMemoryUnitRepository()
        sat_id = uuid4()
        unit = Unit(
            satellite_id=sat_id,
            name="Power",
            description="Power subsystem",
        )

        result = repo.add(unit)

        assert result.id == unit.id
        assert repo.get(unit.id) == unit

    def test_add_duplicate_unit_raises_conflict(self):
        """Test that adding duplicate unit raises ConflictError."""
        repo = InMemoryUnitRepository()
        unit = Unit(
            satellite_id=uuid4(),
            name="Power",
            description="Power subsystem",
        )
        repo.add(unit)

        with pytest.raises(ConflictError, match="already exists"):
            repo.add(unit)

    def test_get_by_satellite(self):
        """Test getting units by satellite ID."""
        repo = InMemoryUnitRepository()
        sat_id = uuid4()
        unit1 = Unit(satellite_id=sat_id, name="Unit1", description="First")
        unit2 = Unit(satellite_id=sat_id, name="Unit2", description="Second")
        unit3 = Unit(satellite_id=uuid4(), name="Unit3", description="Third")

        repo.add(unit1)
        repo.add(unit2)
        repo.add(unit3)

        units = repo.get_by_satellite(sat_id)
        assert len(units) == 2
        assert unit1 in units
        assert unit2 in units
        assert unit3 not in units

    def test_delete_unit_removes_from_index(self):
        """Test that deleting a unit removes it from satellite index."""
        repo = InMemoryUnitRepository()
        sat_id = uuid4()
        unit1 = Unit(satellite_id=sat_id, name="Unit1", description="First")
        unit2 = Unit(satellite_id=sat_id, name="Unit2", description="Second")

        repo.add(unit1)
        repo.add(unit2)

        repo.delete(unit1.id)

        units = repo.get_by_satellite(sat_id)
        assert len(units) == 1
        assert unit1 not in units
        assert unit2 in units


class TestInMemoryParameterRepository:
    """Tests for InMemoryParameterRepository."""

    def test_add_parameter(self):
        """Test adding a parameter."""
        repo = InMemoryParameterRepository()
        unit_id = uuid4()
        param = Parameter(
            unit_id=unit_id,
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
        )

        result = repo.add(param)

        assert result.id == param.id
        assert repo.get(param.id) == param

    def test_add_duplicate_parameter_raises_conflict(self):
        """Test that adding duplicate parameter raises ConflictError."""
        repo = InMemoryParameterRepository()
        param = Parameter(
            unit_id=uuid4(),
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
        )
        repo.add(param)

        with pytest.raises(ConflictError, match="already exists"):
            repo.add(param)

    def test_get_by_unit(self):
        """Test getting parameters by unit ID."""
        repo = InMemoryParameterRepository()
        unit_id = uuid4()
        param1 = Parameter(
            unit_id=unit_id,
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
        )
        param2 = Parameter(
            unit_id=unit_id,
            name="Current",
            unit_of_measurement="A",
            parameter_type=ParameterType.CURRENT,
        )
        param3 = Parameter(
            unit_id=uuid4(),
            name="Temp",
            unit_of_measurement="C",
            parameter_type=ParameterType.TEMPERATURE,
        )

        repo.add(param1)
        repo.add(param2)
        repo.add(param3)

        params = repo.get_by_unit(unit_id)
        assert len(params) == 2
        assert param1 in params
        assert param2 in params
        assert param3 not in params

    def test_delete_parameter_removes_from_index(self):
        """Test that deleting a parameter removes it from unit index."""
        repo = InMemoryParameterRepository()
        unit_id = uuid4()
        param1 = Parameter(
            unit_id=unit_id,
            name="Voltage",
            unit_of_measurement="V",
            parameter_type=ParameterType.VOLTAGE,
        )
        param2 = Parameter(
            unit_id=unit_id,
            name="Current",
            unit_of_measurement="A",
            parameter_type=ParameterType.CURRENT,
        )

        repo.add(param1)
        repo.add(param2)

        repo.delete(param1.id)

        params = repo.get_by_unit(unit_id)
        assert len(params) == 1
        assert param1 not in params
        assert param2 in params


class TestInMemoryTelemetryRepository:
    """Tests for InMemoryTelemetryRepository."""

    def test_add_telemetry(self):
        """Test adding telemetry data."""
        repo = InMemoryTelemetryRepository()
        param_id = uuid4()
        telemetry = TelemetryData(
            parameter_id=param_id,
            timestamp=datetime.now(timezone.utc),
            value=12.5,
        )

        result = repo.add(telemetry)

        assert result.id == telemetry.id
        assert repo.get(telemetry.id) == telemetry

    def test_get_by_parameter_sorted_by_timestamp(self):
        """Test getting telemetry by parameter returns sorted results."""
        repo = InMemoryTelemetryRepository()
        param_id = uuid4()
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Add in random order
        t3 = TelemetryData(
            parameter_id=param_id,
            timestamp=base_time + timedelta(hours=3),
            value=30.0,
        )
        t1 = TelemetryData(
            parameter_id=param_id,
            timestamp=base_time + timedelta(hours=1),
            value=10.0,
        )
        t2 = TelemetryData(
            parameter_id=param_id,
            timestamp=base_time + timedelta(hours=2),
            value=20.0,
        )

        repo.add(t3)
        repo.add(t1)
        repo.add(t2)

        results = repo.get_by_parameter(param_id)

        assert len(results) == 3
        assert results[0].value == 10.0
        assert results[1].value == 20.0
        assert results[2].value == 30.0

    def test_get_by_parameter_with_limit(self):
        """Test getting telemetry with limit returns most recent."""
        repo = InMemoryTelemetryRepository()
        param_id = uuid4()
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        for i in range(10):
            telemetry = TelemetryData(
                parameter_id=param_id,
                timestamp=base_time + timedelta(minutes=i),
                value=float(i),
            )
            repo.add(telemetry)

        results = repo.get_by_parameter(param_id, limit=3)

        assert len(results) == 3
        assert results[0].value == 7.0
        assert results[1].value == 8.0
        assert results[2].value == 9.0

    def test_get_by_parameter_time_range(self):
        """Test getting telemetry within a time range."""
        repo = InMemoryTelemetryRepository()
        param_id = uuid4()
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        for i in range(10):
            telemetry = TelemetryData(
                parameter_id=param_id,
                timestamp=base_time + timedelta(hours=i),
                value=float(i),
            )
            repo.add(telemetry)

        start = base_time + timedelta(hours=3)
        end = base_time + timedelta(hours=6)
        results = repo.get_by_parameter_time_range(param_id, start, end)

        assert len(results) == 4  # Hours 3, 4, 5, 6 (inclusive)
        assert results[0].value == 3.0
        assert results[1].value == 4.0
        assert results[2].value == 5.0
        assert results[3].value == 6.0

    def test_get_by_parameter_different_parameters(self):
        """Test that telemetry is correctly isolated by parameter."""
        repo = InMemoryTelemetryRepository()
        param1 = uuid4()
        param2 = uuid4()
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        t1 = TelemetryData(parameter_id=param1, timestamp=base_time, value=10.0)
        t2 = TelemetryData(parameter_id=param2, timestamp=base_time, value=20.0)

        repo.add(t1)
        repo.add(t2)

        results1 = repo.get_by_parameter(param1)
        results2 = repo.get_by_parameter(param2)

        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0].value == 10.0
        assert results2[0].value == 20.0
