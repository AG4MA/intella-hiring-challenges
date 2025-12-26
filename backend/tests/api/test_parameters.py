"""Tests for parameter API endpoints."""

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
def sample_unit_id(client):
    """Get a unit ID from the initial data."""
    response = client.get("/v1/satellites/")
    satellites = response.json()
    satellite_id = satellites[0]["id"]

    response = client.get(f"/v1/units/?satellite_id={satellite_id}")
    units = response.json()
    return units[0]["id"]


@pytest.fixture
def sample_parameter_id(client, sample_unit_id):
    """Get a parameter ID from the initial data."""
    response = client.get(f"/v1/parameters/?unit_id={sample_unit_id}")
    assert response.status_code == 200
    parameters = response.json()
    assert len(parameters) > 0
    return parameters[0]["id"]


class TestCreateParameter:
    """Tests for POST /v1/parameters/."""

    def test_create_parameter_returns_201(self, client, sample_unit_id):
        """Test creating a parameter returns 201."""
        parameter_data = {
            "unit_id": sample_unit_id,
            "name": "Test Voltage",
            "unit_of_measurement": "V",
            "parameter_type": "voltage",
            "is_active": True,
        }
        response = client.post("/v1/parameters/", json=parameter_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Voltage"
        assert data["unit_of_measurement"] == "V"
        assert data["parameter_type"] == "voltage"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_parameter_with_nonexistent_unit_returns_404(self, client):
        """Test creating parameter with invalid unit returns 404."""
        fake_id = str(uuid4())
        parameter_data = {
            "unit_id": fake_id,
            "name": "Test Parameter",
            "unit_of_measurement": "V",
            "parameter_type": "voltage",
        }
        response = client.post("/v1/parameters/", json=parameter_data)
        assert response.status_code == 404


class TestListParameters:
    """Tests for GET /v1/parameters/."""

    def test_list_all_parameters_returns_200(self, client):
        """Test listing all parameters returns 200."""
        response = client.get("/v1/parameters/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_parameters_by_unit_returns_200(self, client, sample_unit_id):
        """Test listing parameters by unit returns 200."""
        response = client.get(f"/v1/parameters/?unit_id={sample_unit_id}")
        assert response.status_code == 200
        parameters = response.json()
        assert isinstance(parameters, list)
        for param in parameters:
            assert param["unit_id"] == sample_unit_id


class TestGetParameter:
    """Tests for GET /v1/parameters/{parameter_id}."""

    def test_get_parameter_returns_200(self, client, sample_parameter_id):
        """Test getting existing parameter returns 200."""
        response = client.get(f"/v1/parameters/{sample_parameter_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_parameter_id
        assert "name" in data
        assert "unit_of_measurement" in data
        assert "parameter_type" in data
        assert "is_active" in data

    def test_get_nonexistent_parameter_returns_404(self, client):
        """Test getting nonexistent parameter returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/v1/parameters/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()


class TestUpdateParameter:
    """Tests for PUT /v1/parameters/{parameter_id}."""

    def test_update_parameter_name_returns_200(self, client, sample_parameter_id):
        """Test updating parameter name returns 200."""
        response = client.put(
            f"/v1/parameters/{sample_parameter_id}", params={"name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_parameter_unit_returns_200(self, client, sample_parameter_id):
        """Test updating parameter unit returns 200."""
        response = client.put(
            f"/v1/parameters/{sample_parameter_id}",
            params={"unit_of_measurement": "mV"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["unit_of_measurement"] == "mV"

    def test_update_nonexistent_parameter_returns_404(self, client):
        """Test updating nonexistent parameter returns 404."""
        fake_id = str(uuid4())
        response = client.put(f"/v1/parameters/{fake_id}", params={"name": "New Name"})
        assert response.status_code == 404


class TestActivateParameter:
    """Tests for POST /v1/parameters/{parameter_id}/activate."""

    def test_activate_parameter_returns_200(self, client, sample_unit_id):
        """Test activating a parameter returns 200."""
        # Create inactive parameter
        parameter_data = {
            "unit_id": sample_unit_id,
            "name": "Inactive Parameter",
            "unit_of_measurement": "V",
            "parameter_type": "voltage",
            "is_active": False,
        }
        create_response = client.post("/v1/parameters/", json=parameter_data)
        parameter_id = create_response.json()["id"]

        # Activate it
        response = client.post(f"/v1/parameters/{parameter_id}/activate")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    def test_activate_nonexistent_parameter_returns_404(self, client):
        """Test activating nonexistent parameter returns 404."""
        fake_id = str(uuid4())
        response = client.post(f"/v1/parameters/{fake_id}/activate")
        assert response.status_code == 404


class TestDeactivateParameter:
    """Tests for POST /v1/parameters/{parameter_id}/deactivate."""

    def test_deactivate_parameter_returns_200(self, client, sample_parameter_id):
        """Test deactivating a parameter returns 200."""
        # Ensure it's active first
        client.post(f"/v1/parameters/{sample_parameter_id}/activate")

        # Deactivate it
        response = client.post(f"/v1/parameters/{sample_parameter_id}/deactivate")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    def test_deactivate_nonexistent_parameter_returns_404(self, client):
        """Test deactivating nonexistent parameter returns 404."""
        fake_id = str(uuid4())
        response = client.post(f"/v1/parameters/{fake_id}/deactivate")
        assert response.status_code == 404


class TestDeleteParameter:
    """Tests for DELETE /v1/parameters/{parameter_id}."""

    def test_delete_parameter_returns_204(self, client, sample_unit_id):
        """Test deleting a parameter returns 204."""
        # Create parameter to delete
        parameter_data = {
            "unit_id": sample_unit_id,
            "name": "Parameter to Delete",
            "unit_of_measurement": "V",
            "parameter_type": "voltage",
        }
        create_response = client.post("/v1/parameters/", json=parameter_data)
        parameter_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/v1/parameters/{parameter_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/v1/parameters/{parameter_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_parameter_returns_404(self, client):
        """Test deleting nonexistent parameter returns 404."""
        fake_id = str(uuid4())
        response = client.delete(f"/v1/parameters/{fake_id}")
        assert response.status_code == 404
