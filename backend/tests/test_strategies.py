"""Tests for telemetry generation strategies."""

import math
from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.domain.models import ParameterType
from app.workers.strategies import RealisticTelemetryGenerator


@pytest.fixture
def generator():
    """Create deterministic generator for testing."""
    return RealisticTelemetryGenerator(seed=42)


@pytest.fixture
def sample_timestamp():
    """Sample timestamp for testing."""
    return datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_generator_maintains_separate_state_per_parameter(generator, sample_timestamp):
    """Test that each parameter has independent state."""
    param_id_1 = UUID("00000000-0000-0000-0000-000000000001")
    param_id_2 = UUID("00000000-0000-0000-0000-000000000002")

    # Generate values for two parameters
    value_1a = generator.generate(param_id_1, ParameterType.VOLTAGE, sample_timestamp)
    value_2a = generator.generate(param_id_2, ParameterType.VOLTAGE, sample_timestamp)
    value_1b = generator.generate(param_id_1, ParameterType.VOLTAGE, sample_timestamp)

    # Different parameters should have different trajectories
    assert value_1a != value_2a

    # Same parameter should have continuity
    assert abs(value_1b - value_1a) < 1.0  # Small step


def test_voltage_uses_mean_reversion(generator, sample_timestamp):
    """Test voltage strategy with random walk and mean reversion."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate multiple values
    values = [
        generator.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)
        for _ in range(100)
    ]

    # Check realistic bounds
    assert all(10.0 <= v <= 14.0 for v in values), "Voltage out of bounds"

    # Check mean reversion (average should be near nominal 12.5V)
    avg = sum(values) / len(values)
    assert 11.5 <= avg <= 13.5, f"Average {avg} not near nominal 12.5V"

    # Check continuity (no sudden jumps)
    diffs = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
    assert all(d < 0.5 for d in diffs), "Voltage has discontinuous jumps"


def test_temperature_has_diurnal_cycle(generator):
    """Test temperature strategy has daily cycle."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate values at different hours
    morning = datetime(2024, 1, 15, 6, 0, 0, tzinfo=timezone.utc)
    afternoon = datetime(2024, 1, 15, 14, 0, 0, tzinfo=timezone.utc)
    night = datetime(2024, 1, 15, 22, 0, 0, tzinfo=timezone.utc)

    # Reset state for clean test
    generator.reset(param_id)
    temp_morning = generator.generate(param_id, ParameterType.TEMPERATURE, morning)

    generator.reset(param_id)
    temp_afternoon = generator.generate(param_id, ParameterType.TEMPERATURE, afternoon)

    generator.reset(param_id)
    temp_night = generator.generate(param_id, ParameterType.TEMPERATURE, night)

    # Afternoon should be warmer than morning and night
    assert temp_afternoon > temp_morning, "Afternoon should be warmer than morning"
    assert temp_afternoon > temp_night, "Afternoon should be warmer than night"

    # All should be in reasonable range
    assert all(-30 <= t <= 50 for t in [temp_morning, temp_afternoon, temp_night])


def test_current_is_non_negative(generator, sample_timestamp):
    """Test current strategy maintains non-negative values."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate many values
    values = [
        generator.generate(param_id, ParameterType.CURRENT, sample_timestamp)
        for _ in range(100)
    ]

    # All current values must be >= 0
    assert all(v >= 0.0 for v in values), "Current cannot be negative"

    # Should be in realistic range
    assert all(v <= 10.0 for v in values), "Current unrealistically high"


def test_pressure_has_slow_drift(generator, sample_timestamp):
    """Test pressure strategy has slow, continuous drift."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate sequence
    values = [
        generator.generate(param_id, ParameterType.PRESSURE, sample_timestamp)
        for _ in range(50)
    ]

    # Check atmospheric pressure bounds
    assert all(95.0 <= v <= 105.0 for v in values), "Pressure out of bounds"

    # Check for very slow changes (each step should be tiny)
    diffs = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
    assert all(d < 0.5 for d in diffs), "Pressure changes too quickly"


def test_humidity_bounded_to_percentage(generator, sample_timestamp):
    """Test humidity strategy stays within 0-100% range."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate many values
    values = [
        generator.generate(param_id, ParameterType.HUMIDITY, sample_timestamp)
        for _ in range(100)
    ]

    # Humidity must be 0-100%
    assert all(0.0 <= v <= 100.0 for v in values), "Humidity out of percentage range"


def test_power_has_sawtooth_pattern(generator, sample_timestamp):
    """Test power strategy has sawtooth charging/discharging pattern."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate full cycle (50 steps)
    values = [
        generator.generate(param_id, ParameterType.POWER, sample_timestamp)
        for _ in range(60)
    ]

    # Find local minima and maxima
    minima = [
        i
        for i in range(1, len(values) - 1)
        if values[i] < values[i - 1] and values[i] < values[i + 1]
    ]
    maxima = [
        i
        for i in range(1, len(values) - 1)
        if values[i] > values[i - 1] and values[i] > values[i + 1]
    ]

    # Should have at least one cycle (min and max)
    assert len(minima) >= 1, "No discharge phase detected"
    assert len(maxima) >= 1, "No charge phase detected"

    # Power should be non-negative
    assert all(v >= 0.0 for v in values), "Power cannot be negative"


def test_signal_strength_has_occasional_drops(generator, sample_timestamp):
    """Test signal strength has occasional signal drops."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate many values to see drops
    values = [
        generator.generate(param_id, ParameterType.SIGNAL_STRENGTH, sample_timestamp)
        for _ in range(200)
    ]

    # Should be in dBm range
    assert all(-100.0 <= v <= -30.0 for v in values), "Signal strength out of range"

    # Should have some variation (drops)
    value_range = max(values) - min(values)
    assert value_range > 5.0, "Signal strength should have drops"


def test_reset_clears_parameter_state(generator, sample_timestamp):
    """Test that reset clears state for a parameter."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Generate some values to establish state
    value_1 = generator.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)
    value_2 = generator.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)

    # Values should be continuous
    assert abs(value_2 - value_1) < 1.0

    # Reset and generate again
    generator.reset(param_id)
    value_3 = generator.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)

    # After reset, should restart from initial value (may differ significantly)
    # Just check it's a valid value
    assert 10.0 <= value_3 <= 14.0


def test_reset_all_clears_all_state(generator, sample_timestamp):
    """Test that reset_all clears all parameter states."""
    param_ids = [UUID(f"00000000-0000-0000-0000-00000000000{i}") for i in range(1, 4)]

    # Generate values for multiple parameters
    for param_id in param_ids:
        generator.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)

    # Clear all state
    generator.reset_all()

    # Generate again - should restart from initial values
    for param_id in param_ids:
        value = generator.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)
        assert 10.0 <= value <= 14.0  # Valid voltage


def test_deterministic_with_seed(sample_timestamp):
    """Test that same seed produces same values."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    # Create two generators with same seed
    gen1 = RealisticTelemetryGenerator(seed=123)
    gen2 = RealisticTelemetryGenerator(seed=123)

    # Generate sequences
    values1 = [
        gen1.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)
        for _ in range(10)
    ]
    values2 = [
        gen2.generate(param_id, ParameterType.VOLTAGE, sample_timestamp)
        for _ in range(10)
    ]

    # Should be identical
    assert values1 == values2, "Same seed should produce same values"


def test_all_parameter_types_generate_valid_values(generator, sample_timestamp):
    """Test that all parameter types generate valid values."""
    param_id = UUID("00000000-0000-0000-0000-000000000001")

    for param_type in ParameterType:
        # Reset state for clean test
        generator.reset(param_id)

        # Generate value
        value = generator.generate(param_id, param_type, sample_timestamp)

        # Should be a valid finite number
        assert isinstance(value, float), f"{param_type} should generate float"
        assert not math.isnan(value), f"{param_type} generated NaN"
        assert not math.isinf(value), f"{param_type} generated Inf"
