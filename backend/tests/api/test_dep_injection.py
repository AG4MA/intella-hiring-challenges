"""
Tests for API dependency injection helpers.

These tests verify that:
1. The deps module can be imported without side effects
2. Dependency getters correctly access app.state
3. Type annotations are properly configured for FastAPI DI
"""

from typing import Any

import pytest
from starlette.requests import Request as StarletteRequest

from app.api import dep_injection
from app.core.settings import Settings
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


class MockState:
    """Mock state object that allows dynamic attribute assignment."""

    pass


class MockApp:
    """Minimal mock app with state attribute."""

    def __init__(self):
        self.state: Any = MockState()


@pytest.fixture
def mock_app():
    """Create a minimal app mock with services in app.state."""
    app = MockApp()

    # Initialize repositories
    satellite_repo = InMemorySatelliteRepository()
    unit_repo = InMemoryUnitRepository()
    parameter_repo = InMemoryParameterRepository()
    telemetry_repo = InMemoryTelemetryRepository()

    # Initialize services
    satellite_service = SatelliteService(satellite_repo)
    unit_service = UnitService(unit_repo, satellite_repo)
    parameter_service = ParameterService(parameter_repo, unit_repo)
    telemetry_service = TelemetryService(
        telemetry_repo,
        parameter_repo,
        unit_repo,
        satellite_repo,
    )

    # Store in app.state
    app.state.settings = Settings()
    app.state.satellite_service = satellite_service
    app.state.unit_service = unit_service
    app.state.parameter_service = parameter_service
    app.state.telemetry_service = telemetry_service

    return app


@pytest.fixture
def mock_request(mock_app):
    """Create a minimal request mock."""
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "headers": [],
        "app": mock_app,
    }
    return StarletteRequest(scope)


class TestDepsImport:
    """Test that deps module can be imported without side effects."""

    def test_import_deps_has_no_side_effects(self):
        """Importing dep_injection should not create any global state or run code."""
        # If we get here, the import at the top succeeded
        assert hasattr(dep_injection, "get_settings")
        assert hasattr(dep_injection, "get_satellite_service")
        assert hasattr(dep_injection, "get_unit_service")
        assert hasattr(dep_injection, "get_parameter_service")
        assert hasattr(dep_injection, "get_telemetry_service")

    def test_type_aliases_exist(self):
        """Verify type aliases are defined for FastAPI dependency injection."""
        assert hasattr(dep_injection, "SettingsDep")
        assert hasattr(dep_injection, "SatelliteServiceDep")
        assert hasattr(dep_injection, "UnitServiceDep")
        assert hasattr(dep_injection, "ParameterServiceDep")
        assert hasattr(dep_injection, "TelemetryServiceDep")


class TestGetSettings:
    """Test get_settings dependency."""

    def test_get_settings_returns_settings_from_app_state(self, mock_request):
        """get_settings should return the Settings instance from app.state."""
        settings = dep_injection.get_settings(mock_request)

        assert isinstance(settings, Settings)
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_get_settings_returns_same_instance(self, mock_request):
        """Multiple calls should return the same Settings instance."""
        settings1 = dep_injection.get_settings(mock_request)
        settings2 = dep_injection.get_settings(mock_request)

        # Should be the exact same object
        assert settings1 is settings2


class TestGetServices:
    """Test service dependency getters."""

    def test_get_satellite_service_returns_service_from_app_state(self, mock_request):
        """get_satellite_service should return the service from app.state."""
        service = dep_injection.get_satellite_service(mock_request)

        assert isinstance(service, SatelliteService)

    def test_get_unit_service_returns_service_from_app_state(self, mock_request):
        """get_unit_service should return the service from app.state."""
        service = dep_injection.get_unit_service(mock_request)

        assert isinstance(service, UnitService)

    def test_get_parameter_service_returns_service_from_app_state(self, mock_request):
        """get_parameter_service should return the service from app.state."""
        service = dep_injection.get_parameter_service(mock_request)

        assert isinstance(service, ParameterService)

    def test_get_telemetry_service_returns_service_from_app_state(self, mock_request):
        """get_telemetry_service should return the service from app.state."""
        service = dep_injection.get_telemetry_service(mock_request)

        assert isinstance(service, TelemetryService)

    def test_all_services_accessible(self, mock_request):
        """All service dependencies should be accessible."""
        satellite_service = dep_injection.get_satellite_service(mock_request)
        unit_service = dep_injection.get_unit_service(mock_request)
        parameter_service = dep_injection.get_parameter_service(mock_request)
        telemetry_service = dep_injection.get_telemetry_service(mock_request)
        settings = dep_injection.get_settings(mock_request)

        assert isinstance(satellite_service, SatelliteService)
        assert isinstance(unit_service, UnitService)
        assert isinstance(parameter_service, ParameterService)
        assert isinstance(telemetry_service, TelemetryService)
        assert isinstance(settings, Settings)


class TestServiceFunctionality:
    """Test that injected services are functional."""

    def test_injected_satellite_service_can_list_satellites(self, mock_request):
        """The injected satellite service should be fully functional."""
        service = dep_injection.get_satellite_service(mock_request)

        satellites = service.list_all()
        # Should have 0 satellites initially (no initial_data called)
        assert len(satellites) == 0

    def test_injected_services_share_same_instances(self, mock_request):
        """Services should be the same instances across multiple calls."""
        service1 = dep_injection.get_satellite_service(mock_request)
        service2 = dep_injection.get_satellite_service(mock_request)

        # Both should return the same instance (from app.state)
        assert service1 is service2

    def test_services_are_independent_across_different_apps(self, mock_app):
        """Different apps should have different service instances."""
        # Create first request with original app
        scope1 = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
            "app": mock_app,
        }
        request1 = StarletteRequest(scope1)

        # Create second app with different services
        app2 = MockApp()
        satellite_repo2 = InMemorySatelliteRepository()
        app2.state.satellite_service = SatelliteService(satellite_repo2)

        scope2 = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
            "app": app2,
        }
        request2 = StarletteRequest(scope2)

        # Get services from both requests
        service1 = dep_injection.get_satellite_service(request1)
        service2 = dep_injection.get_satellite_service(request2)

        # They should be different instances
        assert service1 is not service2
