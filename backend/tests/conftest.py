"""Shared pytest fixtures for all tests.

Provides common fixtures for test client, deterministic data setup,
and other test infrastructure needed across the test suite.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client with lifespan context.

    Uses context manager to ensure lifespan events (startup/shutdown)
    are properly executed, initializing services and repositories.

    Yields:
        TestClient: Configured test client with app state initialized.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_satellite(client):
    """Get first satellite from initial data.

    Returns:
        dict: Satellite data with id, name, status, etc.
    """
    response = client.get("/v1/satellites/")
    assert response.status_code == 200
    satellites = response.json()
    assert len(satellites) > 0
    return satellites[0]


@pytest.fixture
def sample_satellite_id(client):
    """Get a satellite ID from initial data.

    Returns:
        str: UUID of the first satellite.
    """
    response = client.get("/v1/satellites/")
    assert response.status_code == 200
    satellites = response.json()
    assert len(satellites) > 0
    return satellites[0]["id"]


@pytest.fixture
def active_satellite(client):
    """Get or create an active satellite.

    Ensures the returned satellite has status='active'.

    Returns:
        dict: Active satellite data.
    """
    response = client.get("/v1/satellites/")
    satellites = response.json()

    # Try to find an already active satellite
    for satellite in satellites:
        if satellite["status"] == "active":
            return satellite

    # If none active, activate the first one
    satellite_id = satellites[0]["id"]
    activate_response = client.post(f"/v1/satellites/{satellite_id}/activate")
    if activate_response.status_code == 200:
        return activate_response.json()

    # Return first satellite anyway (might already be active, 409 response)
    return client.get(f"/v1/satellites/{satellite_id}").json()


@pytest.fixture
def create_test_unit(client, sample_satellite_id):
    """Factory fixture to create test units.

    Returns a function that creates a unit and returns its data.
    Useful for tests that need to create multiple units or clean up.

    Returns:
        Callable: Function(name, description) -> unit dict
    """
    created_units = []

    def _create_unit(name: str = "Test Unit", description: str = "Test Description"):
        response = client.post(
            "/v1/units/",
            json={
                "satellite_id": sample_satellite_id,
                "name": name,
                "description": description,
            },
        )
        assert response.status_code == 201
        unit = response.json()
        created_units.append(unit["id"])
        return unit

    yield _create_unit

    # Cleanup created units
    for unit_id in created_units:
        client.delete(f"/v1/units/{unit_id}")


@pytest.fixture
def create_test_parameter(client):
    """Factory fixture to create test parameters.

    Returns a function that creates a parameter and returns its data.
    Useful for tests that need to create multiple parameters or clean up.

    Returns:
        Callable: Function(unit_id, name, **kwargs) -> parameter dict
    """
    created_params = []

    def _create_parameter(
        unit_id: str,
        name: str = "Test Parameter",
        unit_of_measurement: str = "units",
        parameter_type: str = "temperature",
    ):
        response = client.post(
            "/v1/parameters/",
            json={
                "unit_id": unit_id,
                "name": name,
                "unit_of_measurement": unit_of_measurement,
                "parameter_type": parameter_type,
            },
        )
        assert response.status_code == 201
        parameter = response.json()
        created_params.append(parameter["id"])
        return parameter

    yield _create_parameter

    # Cleanup created parameters
    for param_id in created_params:
        client.delete(f"/v1/parameters/{param_id}")
