"""Tests for unit API endpoints."""

from uuid import uuid4

import pytest


@pytest.fixture
def sample_satellite_id(client):
    """Get a satellite ID from the initial data."""
    response = client.get("/v1/satellites/")
    assert response.status_code == 200
    satellites = response.json()
    assert len(satellites) > 0
    return satellites[0]["id"]


@pytest.fixture
def sample_unit_id(client, sample_satellite_id):
    """Get a unit ID from the initial data."""
    response = client.get(f"/v1/units/?satellite_id={sample_satellite_id}")
    assert response.status_code == 200
    units = response.json()
    assert len(units) > 0
    return units[0]["id"]


class TestCreateUnit:
    """Tests for POST /v1/units/."""

    def test_create_unit_returns_201(self, client, sample_satellite_id):
        """Test creating a unit returns 201."""
        unit_data = {
            "satellite_id": sample_satellite_id,
            "name": "Test Unit",
            "description": "Test unit description",
        }
        response = client.post("/v1/units/", json=unit_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Unit"
        assert data["description"] == "Test unit description"
        assert "id" in data

    def test_create_unit_with_nonexistent_satellite_returns_404(self, client):
        """Test creating unit with invalid satellite returns 404."""
        fake_id = str(uuid4())
        unit_data = {
            "satellite_id": fake_id,
            "name": "Test Unit",
            "description": "Test description",
        }
        response = client.post("/v1/units/", json=unit_data)
        assert response.status_code == 404


class TestListUnits:
    """Tests for GET /v1/units/."""

    def test_list_units_returns_200(self, client, sample_satellite_id):
        """Test listing units returns 200."""
        response = client.get(f"/v1/units/?satellite_id={sample_satellite_id}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_units_filters_by_satellite(self, client, sample_satellite_id):
        """Test units are filtered by satellite_id."""
        response = client.get(f"/v1/units/?satellite_id={sample_satellite_id}")
        assert response.status_code == 200
        units = response.json()
        for unit in units:
            assert unit["satellite_id"] == sample_satellite_id


class TestGetUnit:
    """Tests for GET /v1/units/{unit_id}."""

    def test_get_unit_returns_200(self, client, sample_unit_id):
        """Test getting existing unit returns 200."""
        response = client.get(f"/v1/units/{sample_unit_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_unit_id
        assert "name" in data
        assert "description" in data

    def test_get_nonexistent_unit_returns_404(self, client):
        """Test getting nonexistent unit returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/v1/units/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()


class TestUpdateUnit:
    """Tests for PUT /v1/units/{unit_id}."""

    def test_update_unit_name_returns_200(self, client, sample_unit_id):
        """Test updating unit name returns 200."""
        response = client.put(
            f"/v1/units/{sample_unit_id}", params={"name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_unit_description_returns_200(self, client, sample_unit_id):
        """Test updating unit description returns 200."""
        response = client.put(
            f"/v1/units/{sample_unit_id}",
            params={"description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_update_nonexistent_unit_returns_404(self, client):
        """Test updating nonexistent unit returns 404."""
        fake_id = str(uuid4())
        response = client.put(f"/v1/units/{fake_id}", params={"name": "New Name"})
        assert response.status_code == 404


class TestDeleteUnit:
    """Tests for DELETE /v1/units/{unit_id}."""

    def test_delete_unit_returns_204(self, client, sample_satellite_id):
        """Test deleting a unit returns 204."""
        # First create a unit to delete
        unit_data = {
            "satellite_id": sample_satellite_id,
            "name": "Unit to Delete",
            "description": "Will be deleted",
        }
        create_response = client.post("/v1/units/", json=unit_data)
        unit_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/v1/units/{unit_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/v1/units/{unit_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_unit_returns_404(self, client):
        """Test deleting nonexistent unit returns 404."""
        fake_id = str(uuid4())
        response = client.delete(f"/v1/units/{fake_id}")
        assert response.status_code == 404
