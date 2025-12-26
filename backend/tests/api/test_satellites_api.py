"""Tests for satellite API endpoints."""

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
