"""Shared fixtures for integration tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client with lifespan context for integration tests."""
    with TestClient(app) as c:
        yield c
