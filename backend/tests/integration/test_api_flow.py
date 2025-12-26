"""Integration tests for API flow.

Tests the complete flow from API endpoints through services to storage,
verifying that routing, dependency injection, and service wiring work correctly.
"""

from datetime import UTC, datetime
from uuid import uuid4


class TestSatelliteAPIFlow:
    """Integration tests for satellite API flow."""

    def test_list_satellites_with_pagination_flow(self, client):
        """Test complete flow: list satellites with pagination."""
        # Get all satellites
        response_all = client.get("/v1/satellites/?limit=100")
        assert response_all.status_code == 200
        all_satellites = response_all.json()
        assert len(all_satellites) > 0

        # Test pagination - first page
        response_page1 = client.get("/v1/satellites/?skip=0&limit=2")
        assert response_page1.status_code == 200
        page1_data = response_page1.json()
        assert len(page1_data) <= 2

        # Test pagination - second page
        response_page2 = client.get("/v1/satellites/?skip=2&limit=2")
        assert response_page2.status_code == 200
        page2_data = response_page2.json()

        # Verify pagination works correctly
        if len(all_satellites) > 2:
            assert page1_data[0]["id"] != page2_data[0]["id"]

    def test_satellite_activate_disable_state_flow(self, client):
        """Test complete flow: activate/disable satellite and verify state changes."""
        # Get a satellite
        response = client.get("/v1/satellites/")
        assert response.status_code == 200
        satellites = response.json()
        assert len(satellites) > 0
        satellite_id = satellites[0]["id"]

        # Activate satellite
        activate_response = client.post(f"/v1/satellites/{satellite_id}/activate")
        assert activate_response.status_code in [200, 409]  # 409 if already active

        # Verify it's active
        get_response = client.get(f"/v1/satellites/{satellite_id}")
        assert get_response.status_code == 200
        satellite = get_response.json()
        assert satellite["status"] == "active"

        # Disable satellite
        disable_response = client.post(f"/v1/satellites/{satellite_id}/disable")
        assert disable_response.status_code == 200
        disabled_satellite = disable_response.json()
        assert disabled_satellite["status"] == "disabled"

        # Verify state persisted
        get_response2 = client.get(f"/v1/satellites/{satellite_id}")
        assert get_response2.status_code == 200
        satellite2 = get_response2.json()
        assert satellite2["status"] == "disabled"

        # Try to disable again - should fail
        disable_response2 = client.post(f"/v1/satellites/{satellite_id}/disable")
        assert disable_response2.status_code == 409

        # Re-activate for cleanup
        reactivate_response = client.post(f"/v1/satellites/{satellite_id}/activate")
        assert reactivate_response.status_code == 200

    def test_satellite_status_summary_reflects_state(self, client):
        """Test that status summary endpoint reflects satellite state changes."""
        # Get a satellite
        response = client.get("/v1/satellites/")
        satellites = response.json()
        satellite_id = satellites[0]["id"]

        # Get initial status summary
        status_response = client.get("/v1/satellites/status")
        assert status_response.status_code == 200
        summaries = status_response.json()
        initial_summary = next(
            (s for s in summaries if s["satellite_id"] == satellite_id), None
        )
        assert initial_summary is not None

        # Disable satellite
        client.post(f"/v1/satellites/{satellite_id}/disable")

        # Check status summary updated
        status_response2 = client.get("/v1/satellites/status")
        summaries2 = status_response2.json()
        updated_summary = next(
            (s for s in summaries2 if s["satellite_id"] == satellite_id), None
        )
        assert updated_summary is not None
        assert updated_summary["is_active"] is False
        assert updated_summary["operational_status"] == "DISABLED"

        # Re-activate
        client.post(f"/v1/satellites/{satellite_id}/activate")

        # Verify status updated
        status_response3 = client.get("/v1/satellites/status")
        summaries3 = status_response3.json()
        final_summary = next(
            (s for s in summaries3 if s["satellite_id"] == satellite_id), None
        )
        assert final_summary is not None
        assert final_summary["is_active"] is True


class TestUnitParameterAPIFlow:
    """Integration tests for unit and parameter API flow."""

    def test_create_unit_and_parameter_flow(self, client):
        """Test complete flow: create unit, then create parameter for it."""
        # Get a satellite
        satellites_response = client.get("/v1/satellites/")
        assert satellites_response.status_code == 200
        satellites = satellites_response.json()
        satellite_id = satellites[0]["id"]

        # Create a unit
        unit_data = {
            "satellite_id": satellite_id,
            "name": "Integration Test Unit",
            "description": "Unit created in integration test",
        }
        unit_response = client.post("/v1/units/", json=unit_data)
        assert unit_response.status_code == 201
        unit = unit_response.json()
        assert unit["name"] == "Integration Test Unit"
        assert unit["satellite_id"] == satellite_id
        unit_id = unit["id"]

        # Verify unit appears in list
        units_list_response = client.get(f"/v1/units/?satellite_id={satellite_id}")
        assert units_list_response.status_code == 200
        units = units_list_response.json()
        assert any(u["id"] == unit_id for u in units)

        # Create a parameter for the unit
        parameter_data = {
            "unit_id": unit_id,
            "name": "Integration Test Parameter",
            "unit_of_measurement": "celsius",
            "parameter_type": "temperature",
        }
        param_response = client.post("/v1/parameters/", json=parameter_data)
        assert param_response.status_code == 201
        parameter = param_response.json()
        assert parameter["name"] == "Integration Test Parameter"
        assert parameter["unit_id"] == unit_id
        assert parameter["is_active"] is True
        parameter_id = parameter["id"]

        # Verify parameter appears in list
        params_list_response = client.get(f"/v1/parameters/?unit_id={unit_id}")
        assert params_list_response.status_code == 200
        params = params_list_response.json()
        assert any(p["id"] == parameter_id for p in params)

        # Clean up
        client.delete(f"/v1/parameters/{parameter_id}")
        client.delete(f"/v1/units/{unit_id}")

    def test_parameter_activation_flow(self, client):
        """Test complete flow: create parameter, activate/deactivate it."""
        # Setup: create unit and parameter
        satellites_response = client.get("/v1/satellites/")
        satellite_id = satellites_response.json()[0]["id"]

        unit_response = client.post(
            "/v1/units/",
            json={
                "satellite_id": satellite_id,
                "name": "Test Unit Activation",
                "description": "For activation test",
            },
        )
        unit = unit_response.json()
        unit_id = unit["id"]

        param_response = client.post(
            "/v1/parameters/",
            json={
                "unit_id": unit_id,
                "name": "Test Param Activation",
                "unit_of_measurement": "volts",
                "parameter_type": "voltage",
            },
        )
        parameter = param_response.json()
        parameter_id = parameter["id"]
        assert parameter["is_active"] is True

        # Deactivate parameter
        deactivate_response = client.post(f"/v1/parameters/{parameter_id}/deactivate")
        assert deactivate_response.status_code == 200
        deactivated = deactivate_response.json()
        assert deactivated["is_active"] is False

        # Verify state persisted
        get_response = client.get(f"/v1/parameters/{parameter_id}")
        assert get_response.status_code == 200
        param_check = get_response.json()
        assert param_check["is_active"] is False

        # Activate parameter
        activate_response = client.post(f"/v1/parameters/{parameter_id}/activate")
        assert activate_response.status_code == 200
        activated = activate_response.json()
        assert activated["is_active"] is True

        # Clean up
        client.delete(f"/v1/parameters/{parameter_id}")
        client.delete(f"/v1/units/{unit_id}")

    def test_unit_deletion_cascade_validation(self, client):
        """Test that attempting operations on deleted entities returns 404."""
        # Setup
        satellites_response = client.get("/v1/satellites/")
        satellite_id = satellites_response.json()[0]["id"]

        unit_response = client.post(
            "/v1/units/",
            json={
                "satellite_id": satellite_id,
                "name": "Test Unit Delete",
                "description": "For deletion test",
            },
        )
        unit = unit_response.json()
        unit_id = unit["id"]

        # Delete unit
        delete_response = client.delete(f"/v1/units/{unit_id}")
        assert delete_response.status_code == 204

        # Verify GET returns 404
        get_response = client.get(f"/v1/units/{unit_id}")
        assert get_response.status_code == 404

        # Verify UPDATE returns 404
        update_response = client.put(
            f"/v1/units/{unit_id}",
            json={
                "satellite_id": satellite_id,
                "name": "Updated Name",
                "description": "Updated",
            },
        )
        assert update_response.status_code == 404


class TestTelemetryAPIFlow:
    """Integration tests for telemetry API flow."""

    def test_telemetry_query_with_filters_and_pagination(self, client):
        """Test complete flow: insert telemetry, query with filters and pagination."""
        # Setup: create parameter for telemetry
        satellites_response = client.get("/v1/satellites/")
        satellites = satellites_response.json()
        # Get an active satellite
        active_satellite = next(
            (s for s in satellites if s["status"] == "active"), None
        )
        if not active_satellite:
            # Activate first satellite
            satellite_id = satellites[0]["id"]
            client.post(f"/v1/satellites/{satellite_id}/activate")
            active_satellite = client.get(f"/v1/satellites/{satellite_id}").json()

        satellite_id = active_satellite["id"]

        # Create unit and parameter
        unit_response = client.post(
            "/v1/units/",
            json={
                "satellite_id": satellite_id,
                "name": "Telemetry Test Unit",
                "description": "For telemetry flow test",
            },
        )
        unit = unit_response.json()
        unit_id = unit["id"]

        param_response = client.post(
            "/v1/parameters/",
            json={
                "unit_id": unit_id,
                "name": "Telemetry Test Param",
                "unit_of_measurement": "celsius",
                "parameter_type": "temperature",
            },
        )
        parameter = param_response.json()
        parameter_id = parameter["id"]

        # Activate parameter
        client.post(f"/v1/parameters/{parameter_id}/activate")

        # Insert deterministic telemetry data via service
        from app.domain.models import TelemetryData

        telemetry_service = client.app.state.telemetry_service

        timestamps = [
            datetime(2024, 6, 1, 10, 0, 0, tzinfo=UTC),
            datetime(2024, 6, 1, 10, 5, 0, tzinfo=UTC),
            datetime(2024, 6, 1, 10, 10, 0, tzinfo=UTC),
            datetime(2024, 6, 1, 10, 15, 0, tzinfo=UTC),
            datetime(2024, 6, 1, 10, 20, 0, tzinfo=UTC),
        ]

        for i, ts in enumerate(timestamps):
            telemetry = TelemetryData(
                id=uuid4(),
                parameter_id=parameter_id,
                timestamp=ts,
                value=20.0 + i,
            )
            telemetry_service._repo.add(telemetry)

        # Test 1: Query without filters
        response_all = client.get(f"/v1/telemetry?parameter_id={parameter_id}")
        assert response_all.status_code == 200
        all_data = response_all.json()
        assert len(all_data) >= 5

        # Test 2: Query with time range filter
        from_ts = (
            datetime(2024, 6, 1, 10, 5, 0, tzinfo=UTC)
            .isoformat()
            .replace("+00:00", "Z")
        )
        to_ts = (
            datetime(2024, 6, 1, 10, 15, 0, tzinfo=UTC)
            .isoformat()
            .replace("+00:00", "Z")
        )

        response_filtered = client.get(
            f"/v1/telemetry?parameter_id={parameter_id}&from_ts={from_ts}&to_ts={to_ts}"
        )
        assert response_filtered.status_code == 200
        filtered_data = response_filtered.json()
        # Should have 3 points: 10:05, 10:10, 10:15
        assert len([d for d in filtered_data if parameter_id == d["parameter_id"]]) >= 3

        # Test 3: Query with pagination
        response_page1 = client.get(
            f"/v1/telemetry?parameter_id={parameter_id}&limit=2&offset=0"
        )
        assert response_page1.status_code == 200
        page1_data = response_page1.json()
        assert len(page1_data) <= 2

        response_page2 = client.get(
            f"/v1/telemetry?parameter_id={parameter_id}&limit=2&offset=2"
        )
        assert response_page2.status_code == 200
        page2_data = response_page2.json()
        assert len(page2_data) <= 2

        # Verify pagination returns different data
        if len(page1_data) > 0 and len(page2_data) > 0:
            assert page1_data[0]["id"] != page2_data[0]["id"]

        # Test 4: Query with ordering (desc is default)
        response_desc = client.get(
            f"/v1/telemetry?parameter_id={parameter_id}&order=desc&limit=5"
        )
        assert response_desc.status_code == 200
        desc_data = response_desc.json()
        if len(desc_data) >= 2:
            # Verify descending order
            ts1 = datetime.fromisoformat(
                desc_data[0]["timestamp"].replace("Z", "+00:00")
            )
            ts2 = datetime.fromisoformat(
                desc_data[1]["timestamp"].replace("Z", "+00:00")
            )
            assert ts1 >= ts2

        # Test 5: Query with ascending order
        response_asc = client.get(
            f"/v1/telemetry?parameter_id={parameter_id}&order=asc&limit=5"
        )
        assert response_asc.status_code == 200
        asc_data = response_asc.json()
        if len(asc_data) >= 2:
            # Verify ascending order
            ts1 = datetime.fromisoformat(
                asc_data[0]["timestamp"].replace("Z", "+00:00")
            )
            ts2 = datetime.fromisoformat(
                asc_data[1]["timestamp"].replace("Z", "+00:00")
            )
            assert ts1 <= ts2

        # Clean up
        client.delete(f"/v1/parameters/{parameter_id}")
        client.delete(f"/v1/units/{unit_id}")

    def test_telemetry_query_validation(self, client):
        """Test telemetry query endpoint validation."""
        # Test 1: Query without parameter_id returns empty list
        response = client.get("/v1/telemetry")
        assert response.status_code == 200
        assert response.json() == []

        # Test 2: Query with non-existent parameter returns 404
        fake_param_id = str(uuid4())
        response = client.get(f"/v1/telemetry?parameter_id={fake_param_id}")
        assert response.status_code == 404

        # Test 3: Query with invalid limit
        response = client.get("/v1/telemetry?limit=-1")
        assert response.status_code == 422

        # Test 4: Query with limit exceeding max
        response = client.get("/v1/telemetry?limit=20000")
        assert response.status_code == 422

        # Test 5: Query with negative offset
        response = client.get("/v1/telemetry?offset=-1")
        assert response.status_code == 422


class TestCrossEntityAPIFlow:
    """Integration tests for flows across multiple entity types."""

    def test_satellite_to_telemetry_complete_flow(self, client):
        """Test complete flow from satellite to telemetry query."""
        # Step 1: Get and activate satellite
        satellites_response = client.get("/v1/satellites/")
        satellite = satellites_response.json()[0]
        satellite_id = satellite["id"]

        activate_response = client.post(f"/v1/satellites/{satellite_id}/activate")
        assert activate_response.status_code in [200, 409]

        # Step 2: Create unit for satellite
        unit_response = client.post(
            "/v1/units/",
            json={
                "satellite_id": satellite_id,
                "name": "Complete Flow Unit",
                "description": "End-to-end test unit",
            },
        )
        assert unit_response.status_code == 201
        unit = unit_response.json()
        unit_id = unit["id"]

        # Step 3: Create parameter for unit
        param_response = client.post(
            "/v1/parameters/",
            json={
                "unit_id": unit_id,
                "name": "Complete Flow Parameter",
                "unit_of_measurement": "meters",
                "parameter_type": "pressure",
            },
        )
        assert param_response.status_code == 201
        parameter = param_response.json()
        parameter_id = parameter["id"]

        # Step 4: Activate parameter
        activate_param_response = client.post(f"/v1/parameters/{parameter_id}/activate")
        assert activate_param_response.status_code in [200, 409]

        # Step 5: Add telemetry via service
        from app.domain.models import TelemetryData

        telemetry_service = client.app.state.telemetry_service
        test_timestamp = datetime(2024, 7, 1, 15, 30, 0, tzinfo=UTC)

        telemetry = TelemetryData(
            id=uuid4(),
            parameter_id=parameter_id,
            timestamp=test_timestamp,
            value=42.5,
        )
        telemetry_service._repo.add(telemetry)

        # Step 6: Query telemetry
        query_response = client.get(f"/v1/telemetry?parameter_id={parameter_id}")
        assert query_response.status_code == 200
        telemetry_data = query_response.json()
        assert len(telemetry_data) > 0
        assert any(t["value"] == 42.5 for t in telemetry_data)

        # Step 7: Verify status summary reflects all data
        status_response = client.get("/v1/satellites/status")
        summaries = status_response.json()
        sat_summary = next(
            (s for s in summaries if s["satellite_id"] == satellite_id), None
        )
        assert sat_summary is not None
        assert sat_summary["units_count"] > 0
        assert sat_summary["parameters_count"] > 0
        assert sat_summary["telemetry_points_count"] > 0
        assert sat_summary["operational_status"] == "OK"

        # Clean up
        client.delete(f"/v1/parameters/{parameter_id}")
        client.delete(f"/v1/units/{unit_id}")

    def test_error_propagation_across_layers(self, client):
        """Test that errors propagate correctly from service to API layer."""
        # Test 1: Creating parameter for non-existent unit
        fake_unit_id = str(uuid4())
        param_response = client.post(
            "/v1/parameters/",
            json={
                "unit_id": fake_unit_id,
                "name": "Invalid Parameter",
                "unit_of_measurement": "units",
                "parameter_type": "temperature",
            },
        )
        assert param_response.status_code == 404
        assert "not found" in param_response.json()["message"].lower()

        # Test 2: Creating unit for non-existent satellite
        fake_sat_id = str(uuid4())
        unit_response = client.post(
            "/v1/units/",
            json={
                "satellite_id": fake_sat_id,
                "name": "Invalid Unit",
                "description": "Should fail",
            },
        )
        assert unit_response.status_code == 404

        # Test 3: Updating non-existent entity
        fake_param_id = str(uuid4())
        update_response = client.put(
            f"/v1/parameters/{fake_param_id}",
            json={
                "unit_id": fake_sat_id,
                "name": "Updated",
                "unit_of_measurement": "m",
                "parameter_type": "temperature",
            },
        )
        assert update_response.status_code == 404

        # Test 4: Activating non-existent parameter
        activate_response = client.post(f"/v1/parameters/{fake_param_id}/activate")
        assert activate_response.status_code == 404
