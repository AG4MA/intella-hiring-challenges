"""Tests for telemetry query API endpoints."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def telemetry_setup(client):
    """Setup test telemetry data."""
    # Get existing parameter from initial data
    response = client.get("/v1/parameters/")
    parameters = response.json()
    assert len(parameters) > 0

    # Find an active parameter
    active_param = None
    for param in parameters:
        if param["is_active"]:
            active_param = param
            break

    assert active_param is not None, "No active parameters found"
    parameter_id = active_param["id"]

    # Create test telemetry data via service (using the existing generator data)
    # Just return the parameter_id to query existing data
    return {"parameter_id": parameter_id}


class TestQueryTelemetry:
    """Tests for GET /v1/telemetry/."""

    def test_query_without_parameter_returns_empty_list(self, client):
        """Test querying without parameter_id returns empty list."""
        response = client.get("/v1/telemetry/")
        assert response.status_code == 200
        assert response.json() == []

    def test_query_with_parameter_returns_data(self, client, telemetry_setup):
        """Test querying with parameter_id returns telemetry data."""
        parameter_id = telemetry_setup["parameter_id"]
        response = client.get(f"/v1/telemetry/?parameter_id={parameter_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have data from the generator backfill
        assert len(data) > 0
        # Verify structure
        if len(data) > 0:
            item = data[0]
            assert "id" in item
            assert "parameter_id" in item
            assert "timestamp" in item
            assert "value" in item

    def test_query_with_invalid_parameter_returns_404(self, client):
        """Test querying with nonexistent parameter returns 404."""
        from uuid import uuid4

        fake_id = str(uuid4())
        response = client.get(f"/v1/telemetry/?parameter_id={fake_id}")
        assert response.status_code == 404

    def test_query_default_order_is_desc(self, client, telemetry_setup):
        """Test default ordering is descending (newest first)."""
        parameter_id = telemetry_setup["parameter_id"]
        response = client.get(f"/v1/telemetry/?parameter_id={parameter_id}&limit=10")
        assert response.status_code == 200
        data = response.json()
        if len(data) >= 2:
            # Verify descending order (newest first)
            timestamps = [datetime.fromisoformat(item["timestamp"]) for item in data]
            for i in range(len(timestamps) - 1):
                assert timestamps[i] >= timestamps[i + 1]

    def test_query_with_asc_order(self, client, telemetry_setup):
        """Test ascending order returns oldest first."""
        parameter_id = telemetry_setup["parameter_id"]
        response = client.get(
            f"/v1/telemetry/?parameter_id={parameter_id}&order=asc&limit=10"
        )
        assert response.status_code == 200
        data = response.json()
        if len(data) >= 2:
            # Verify ascending order (oldest first)
            timestamps = [datetime.fromisoformat(item["timestamp"]) for item in data]
            for i in range(len(timestamps) - 1):
                assert timestamps[i] <= timestamps[i + 1]

    def test_query_with_limit(self, client, telemetry_setup):
        """Test limit parameter restricts results."""
        parameter_id = telemetry_setup["parameter_id"]
        response = client.get(f"/v1/telemetry/?parameter_id={parameter_id}&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_query_with_offset(self, client, telemetry_setup):
        """Test offset parameter skips records."""
        parameter_id = telemetry_setup["parameter_id"]

        # Get first page
        response1 = client.get(
            f"/v1/telemetry/?parameter_id={parameter_id}&limit=5&offset=0"
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Get second page
        response2 = client.get(
            f"/v1/telemetry/?parameter_id={parameter_id}&limit=5&offset=5"
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Verify different results (if enough data)
        if len(data1) > 0 and len(data2) > 0:
            assert data1[0]["id"] != data2[0]["id"]

    def test_query_with_time_range(self, client, telemetry_setup):
        """Test filtering by time range."""
        parameter_id = telemetry_setup["parameter_id"]

        # Get all data first to find time range
        response = client.get(f"/v1/telemetry/?parameter_id={parameter_id}&limit=1000")
        assert response.status_code == 200
        all_data = response.json()

        if len(all_data) >= 2:
            # Get timestamps
            timestamps = [
                datetime.fromisoformat(item["timestamp"]) for item in all_data
            ]
            min_ts = min(timestamps)
            max_ts = max(timestamps)

            # Query middle range
            mid_point = min_ts + (max_ts - min_ts) / 2
            from_ts = mid_point - timedelta(hours=1)
            to_ts = mid_point + timedelta(hours=1)

            # Format timestamps as ISO strings (replacing '+00:00' with 'Z')
            from_ts_str = from_ts.isoformat().replace("+00:00", "Z")
            to_ts_str = to_ts.isoformat().replace("+00:00", "Z")

            response = client.get(
                f"/v1/telemetry/?parameter_id={parameter_id}"
                f"&from_ts={from_ts_str}&to_ts={to_ts_str}"
            )
            assert response.status_code == 200
            filtered_data = response.json()

            # Should have fewer results than all data
            assert len(filtered_data) <= len(all_data)

            # All timestamps should be in range
            for item in filtered_data:
                ts = datetime.fromisoformat(item["timestamp"])
                assert from_ts <= ts <= to_ts

    def test_query_respects_max_limit(self, client, telemetry_setup):
        """Test limit cannot exceed maximum."""
        parameter_id = telemetry_setup["parameter_id"]
        # Try to request more than max (10000)
        response = client.get(f"/v1/telemetry/?parameter_id={parameter_id}&limit=20000")
        # Should return 422 for invalid parameter
        assert response.status_code == 422

    def test_query_with_negative_offset_returns_422(self, client, telemetry_setup):
        """Test negative offset returns validation error."""
        parameter_id = telemetry_setup["parameter_id"]
        response = client.get(f"/v1/telemetry/?parameter_id={parameter_id}&offset=-1")
        assert response.status_code == 422
