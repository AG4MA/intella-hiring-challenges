"""Enumeration types for the satellite telemetry domain."""

from enum import Enum


class SatelliteStatus(str, Enum):
    """Operational status of a satellite.

    Attributes:
        ACTIVE: Satellite is operational and transmitting data.
        DISABLED: Satellite is offline or decommissioned.
    """

    ACTIVE = "active"
    DISABLED = "disabled"


class ParameterType(str, Enum):
    """Type classification for telemetry parameters.

    Attributes:
        VOLTAGE: Electrical voltage measurement.
        TEMPERATURE: Temperature measurement.
        CURRENT: Electrical current measurement.
        PRESSURE: Pressure measurement.
        HUMIDITY: Humidity measurement.
        POWER: Power consumption measurement.
        SIGNAL_STRENGTH: Radio signal strength measurement.
    """

    VOLTAGE = "voltage"
    TEMPERATURE = "temperature"
    CURRENT = "current"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"
    POWER = "power"
    SIGNAL_STRENGTH = "signal_strength"
