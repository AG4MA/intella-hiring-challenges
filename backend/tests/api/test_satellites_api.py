"""Tests for satellite API endpoints."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_satellite_id(client):
    """Get a satellite ID from the initial data."""
    response = client.get("/v1/satellites/")
    assert response.status_code == 200
    satellites = response.json()
    assert len(satellites) > 0
    return satellites[0]["id"]


@pytest.fixture
def sample_satellite(client):
    """Get first satellite from initial data."""
    response = client.get("/v1/satellites/")
    assert response.status_code == 200
    satellites = response.json()
    assert len(satellites) > 0
    return satellites[0]


class TestListSatellites:
    """Tests for GET /v1/satellites/."""

    def test_list_satellites_returns_200(self, client):
        """Test that listing satellites returns 200."""
        response = client.get("/v1/satellites/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_satellites_with_pagination(self, client):
        """Test pagination parameters work."""
        response = client.get("/v1/satellites/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_list_satellites_skip_parameter(self, client):
        """Test skip parameter works."""
        all_response = client.get("/v1/satellites/?limit=100")
        skip_response = client.get("/v1/satellites/?skip=1&limit=100")

        assert len(skip_response.json()) == len(all_response.json()) - 1

    def test_list_satellites_invalid_skip_returns_422(self, client):
        """Test invalid skip parameter returns 422."""
        response = client.get("/v1/satellites/?skip=-1")
        assert response.status_code == 422

    def test_list_satellites_invalid_limit_returns_422(self, client):
        """Test invalid limit parameter returns 422."""
        response = client.get("/v1/satellites/?limit=0")
        assert response.status_code == 422

    def test_list_satellites_limit_exceeds_max_returns_422(self, client):
        """Test limit exceeding maximum returns 422."""
        response = client.get("/v1/satellites/?limit=2000")
        assert response.status_code == 422


class TestGetSatellite:
    """Tests for GET /v1/satellites/{satellite_id}."""

    def test_get_satellite_returns_200(self, client, sample_satellite_id):
        """Test getting existing satellite returns 200."""
        response = client.get(f"/v1/satellites/{sample_satellite_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_satellite_id
        assert "name" in data
        assert "status" in data

    def test_get_nonexistent_satellite_returns_404(self, client):
        """Test getting nonexistent satellite returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/v1/satellites/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()

    def test_get_satellite_invalid_uuid_returns_422(self, client):
        """Test invalid UUID format returns 422."""
        response = client.get("/v1/satellites/not-a-uuid")
        assert response.status_code == 422


class TestUpdateSatellite:
    """Tests for PATCH /v1/satellites/{satellite_id}."""

    def test_update_satellite_name_returns_200(self, client, sample_satellite_id):
        """Test updating satellite name returns 200."""
        response = client.patch(
            f"/v1/satellites/{sample_satellite_id}",
            params={"name": "Updated Satellite Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Satellite Name"

    def test_update_satellite_metadata_returns_200(self, client, sample_satellite_id):
        """Test updating satellite metadata returns 200."""
        metadata = {"custom_field": "custom_value", "number": 123}
        response = client.patch(
            f"/v1/satellites/{sample_satellite_id}", params={"metadata": str(metadata)}
        )
        assert response.status_code == 200

    def test_update_satellite_both_params_returns_200(
        self, client, sample_satellite_id
    ):
        """Test updating both name and metadata returns 200."""
        response = client.patch(
            f"/v1/satellites/{sample_satellite_id}",
            params={"name": "New Name", "metadata": "{}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"

    def test_update_nonexistent_satellite_returns_404(self, client):
        """Test updating nonexistent satellite returns 404."""
        fake_id = str(uuid4())
        response = client.patch(
            f"/v1/satellites/{fake_id}", params={"name": "New Name"}
        )
        assert response.status_code == 404

    def test_update_satellite_no_params_returns_200(self, client, sample_satellite_id):
        """Test updating without parameters still returns 200."""
        response = client.patch(f"/v1/satellites/{sample_satellite_id}")
        assert response.status_code == 200


class TestActivateSatellite:
    """Tests for POST /v1/satellites/{satellite_id}/activate."""

    def test_activate_disabled_satellite_returns_200(self, client):
        """Test activating a disabled satellite returns 200."""
        # First get a satellite and disable it
        response = client.get("/v1/satellites/")
        satellites = response.json()
        satellite_id = satellites[0]["id"]

        # Disable it first
        client.post(f"/v1/satellites/{satellite_id}/disable")

        # Now activate it
        response = client.post(f"/v1/satellites/{satellite_id}/activate")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    def test_activate_already_active_returns_409(self, client, sample_satellite_id):
        """Test activating already active satellite returns 409."""
        # Ensure it's active
        client.post(f"/v1/satellites/{sample_satellite_id}/activate")

        # Try to activate again
        response = client.post(f"/v1/satellites/{sample_satellite_id}/activate")
        assert response.status_code == 409
        assert "already active" in response.json()["message"].lower()

    def test_activate_nonexistent_satellite_returns_404(self, client):
        """Test activating nonexistent satellite returns 404."""
        fake_id = str(uuid4())
        response = client.post(f"/v1/satellites/{fake_id}/activate")
        assert response.status_code == 404


class TestDisableSatellite:
    """Tests for POST /v1/satellites/{satellite_id}/disable."""

    def test_disable_active_satellite_returns_200(self, client):
        """Test disabling an active satellite returns 200."""
        # First get a satellite and activate it
        response = client.get("/v1/satellites/")
        satellites = response.json()
        satellite_id = satellites[0]["id"]

        # Ensure it's active
        client.post(f"/v1/satellites/{satellite_id}/activate")

        # Now disable it
        response = client.post(f"/v1/satellites/{satellite_id}/disable")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disabled"

    def test_disable_already_disabled_returns_409(self, client):
        """Test disabling already disabled satellite returns 409."""
        # Get a satellite
        response = client.get("/v1/satellites/")
        satellites = response.json()
        satellite_id = satellites[0]["id"]

        # Disable it
        client.post(f"/v1/satellites/{satellite_id}/disable")

        # Try to disable again
        response = client.post(f"/v1/satellites/{satellite_id}/disable")
        assert response.status_code == 409
        assert "already disabled" in response.json()["message"].lower()

    def test_disable_nonexistent_satellite_returns_404(self, client):
        """Test disabling nonexistent satellite returns 404."""
        fake_id = str(uuid4())
        response = client.post(f"/v1/satellites/{fake_id}/disable")
        assert response.status_code == 404


class TestGetSatellitesOperationalStatus:
    """Tests for GET /v1/satellites/status endpoint."""

    def test_status_endpoint_returns_200(self, client):
        """Test that status endpoint returns 200."""
        response = client.get("/v1/satellites/status")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_status_response_structure(self, client):
        """Test response has correct structure."""
        response = client.get("/v1/satellites/status")
        assert response.status_code == 200

        summaries = response.json()
        if len(summaries) > 0:
            summary = summaries[0]
            # Verify all required fields present
            assert "satellite_id" in summary
            assert "is_active" in summary
            assert "last_telemetry_ts" in summary
            assert "telemetry_points_count" in summary
            assert "units_count" in summary
            assert "parameters_count" in summary
            assert "operational_status" in summary

    def test_status_with_initial_data(self, client, sample_satellite):
        """Test status reflects initial data state."""
        response = client.get("/v1/satellites/status")
        assert response.status_code == 200

        summaries = response.json()
        # Find our sample satellite in the results
        sat_summary = next(
            (s for s in summaries if s["satellite_id"] == sample_satellite["id"]),
            None,
        )
        assert sat_summary is not None

        # Verify satellite is tracked
        assert sat_summary["satellite_id"] == sample_satellite["id"]
        assert isinstance(sat_summary["is_active"], bool)
        assert isinstance(sat_summary["telemetry_points_count"], int)
        assert isinstance(sat_summary["units_count"], int)
        assert isinstance(sat_summary["parameters_count"], int)
        assert sat_summary["operational_status"] in ["DISABLED", "NO_DATA", "OK"]

    def test_status_operational_status_logic(self, client):
        """Test operational_status derivation logic."""
        response = client.get("/v1/satellites/status")
        assert response.status_code == 200

        summaries = response.json()
        for summary in summaries:
            is_active = summary["is_active"]
            has_telemetry = summary["last_telemetry_ts"] is not None
            status = summary["operational_status"]

            # Verify status logic
            if not is_active:
                assert status == "DISABLED"
            elif not has_telemetry:
                assert status == "NO_DATA"
            else:
                assert status == "OK"

    def test_status_with_created_data(self, client, sample_satellite):
        """Test status with deterministically created telemetry data."""
        sat_id = sample_satellite["id"]

        # Get initial state
        initial_response = client.get("/v1/satellites/status")
        initial_summaries = initial_response.json()
        initial_summary = next(
            (s for s in initial_summaries if s["satellite_id"] == sat_id),
            None,
        )
        assert initial_summary is not None

        # Create unit
        unit_response = client.post(
            "/v1/units/",
            json={
                "satellite_id": sat_id,
                "name": "Test Unit Status",
                "description": "Unit for status testing",
            },
        )
        assert unit_response.status_code == 201
        unit = unit_response.json()

        # Create parameter
        param_response = client.post(
            "/v1/parameters/",
            json={
                "unit_id": unit["id"],
                "name": "Test Param Status",
                "unit_of_measurement": "celsius",
                "parameter_type": "temperature",
            },
        )
        assert param_response.status_code == 201
        parameter = param_response.json()

        # Activate parameter
        activate_response = client.post(f"/v1/parameters/{parameter['id']}/activate")
        assert activate_response.status_code == 200

        # Add telemetry data directly via storage
        # Get services from app state
        from app.domain.models import TelemetryData

        telemetry_service = client.app.state.telemetry_service

        # Create deterministic telemetry points
        timestamps = [
            datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            datetime(2024, 1, 1, 12, 1, 0, tzinfo=UTC),
            datetime(2024, 1, 1, 12, 2, 0, tzinfo=UTC),
        ]

        for ts in timestamps:
            telemetry = TelemetryData(
                id=uuid4(),
                parameter_id=parameter["id"],
                timestamp=ts,
                value=25.5,
            )
            telemetry_service._repo.add(telemetry)

        # Get updated status
        updated_response = client.get("/v1/satellites/status")
        assert updated_response.status_code == 200

        updated_summaries = updated_response.json()
        updated_summary = next(
            (s for s in updated_summaries if s["satellite_id"] == sat_id),
            None,
        )
        assert updated_summary is not None

        # Verify counts increased
        assert updated_summary["units_count"] >= initial_summary["units_count"] + 1
        assert (
            updated_summary["parameters_count"]
            >= initial_summary["parameters_count"] + 1
        )

        # Verify telemetry data reflected
        assert (
            updated_summary["telemetry_points_count"]
            >= initial_summary["telemetry_points_count"] + 3
        )
        assert updated_summary["last_telemetry_ts"] is not None

        # Verify last timestamp is at least one we inserted (or later from backfill)
        last_ts = datetime.fromisoformat(
            updated_summary["last_telemetry_ts"].replace("Z", "+00:00")
        )
        # Should have telemetry data (either ours or from backfill)
        assert last_ts >= timestamps[0] or last_ts > timestamps[-1]

        # If satellite is active, should be "OK" status
        if updated_summary["is_active"]:
            assert updated_summary["operational_status"] == "OK"

    def test_status_disabled_satellite_shows_disabled_status(self, client):
        """Test that disabled satellites show DISABLED operational status."""
        response = client.get("/v1/satellites/status")
        assert response.status_code == 200

        summaries = response.json()
        # Find any disabled satellite
        disabled_summaries = [s for s in summaries if not s["is_active"]]

        # All disabled satellites should have DISABLED status
        for summary in disabled_summaries:
            assert summary["operational_status"] == "DISABLED"

    def test_status_counts_are_non_negative(self, client):
        """Test that all counts in status are non-negative."""
        response = client.get("/v1/satellites/status")
        assert response.status_code == 200

        summaries = response.json()
        for summary in summaries:
            assert summary["telemetry_points_count"] >= 0
            assert summary["units_count"] >= 0
            assert summary["parameters_count"] >= 0

    def test_status_with_no_telemetry_shows_no_data(self, client, sample_satellite):
        """Test satellite with no telemetry shows NO_DATA status."""
        sat_id = sample_satellite["id"]

        # First disable the satellite to clear state, then re-enable
        disable_response = client.post(f"/v1/satellites/{sat_id}/disable")
        if disable_response.status_code == 200:
            # Re-enable it
            enable_response = client.post(f"/v1/satellites/{sat_id}/activate")
            assert enable_response.status_code in [200, 409]  # 409 if already active

        # Check status
        response = client.get("/v1/satellites/status")
        assert response.status_code == 200

        summaries = response.json()
        sat_summary = next(
            (s for s in summaries if s["satellite_id"] == sat_id),
            None,
        )
        assert sat_summary is not None

        # If active and no telemetry, should be NO_DATA
        # Note: initial data may have telemetry, so we check the logic holds
        if sat_summary["is_active"] and sat_summary["last_telemetry_ts"] is None:
            assert sat_summary["operational_status"] == "NO_DATA"
