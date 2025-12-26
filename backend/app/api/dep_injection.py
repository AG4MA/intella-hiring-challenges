"""Dependency injection helpers for API layer.

Provides FastAPI dependencies to access application settings and services
from app.state without coupling routes to implementation details.
"""

from typing import Annotated

from fastapi import Depends, Request

from app.core.settings import Settings
from app.services.parameter import ParameterService
from app.services.satellite import SatelliteService
from app.services.telemetry import TelemetryService
from app.services.unit import UnitService


def get_settings(request: Request) -> Settings:
    """Get application settings from app state.

    Args:
        request: FastAPI request object.

    Returns:
        Application settings instance.

    Example:
        ```python
        @app.get("/some-endpoint")
        def endpoint(settings: Annotated[Settings, Depends(get_settings)]):
            return {"debug": settings.debug}
        ```
    """
    return request.app.state.settings


def get_satellite_service(request: Request) -> SatelliteService:
    """Get satellite service from app state.

    Args:
        request: FastAPI request object.

    Returns:
        Satellite service instance.
    """
    return request.app.state.satellite_service


def get_unit_service(request: Request) -> UnitService:
    """Get unit service from app state.

    Args:
        request: FastAPI request object.

    Returns:
        Unit service instance.
    """
    return request.app.state.unit_service


def get_parameter_service(request: Request) -> ParameterService:
    """Get parameter service from app state.

    Args:
        request: FastAPI request object.

    Returns:
        Parameter service instance.
    """
    return request.app.state.parameter_service


def get_telemetry_service(request: Request) -> TelemetryService:
    """Get telemetry service from app state.

    Args:
        request: FastAPI request object.

    Returns:
        Telemetry service instance.
    """
    return request.app.state.telemetry_service


# Type aliases for common dependency annotations
SettingsDep = Annotated[Settings, Depends(get_settings)]
SatelliteServiceDep = Annotated[SatelliteService, Depends(get_satellite_service)]
UnitServiceDep = Annotated[UnitService, Depends(get_unit_service)]
ParameterServiceDep = Annotated[ParameterService, Depends(get_parameter_service)]
TelemetryServiceDep = Annotated[TelemetryService, Depends(get_telemetry_service)]
