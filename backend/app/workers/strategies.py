"""Realistic telemetry generation strategies.

Each strategy produces continuous, realistic values for different parameter types.
State is maintained per parameter_id to ensure smooth trajectories.
"""

import math
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.models import ParameterType


@dataclass
class GeneratorState:
    """State for a single parameter's value generation."""

    current_value: float
    """Current value in the trajectory."""

    step_count: int = 0
    """Number of steps since initialization."""

    phase: float = 0.0
    """Phase for cyclical patterns (radians)."""


class GenerationStrategy(Protocol):
    """Protocol for telemetry generation strategies."""

    def generate(
        self,
        parameter_id: UUID,
        parameter_type: ParameterType,
        timestamp: datetime,
    ) -> float:
        """Generate next value for a parameter.

        Args:
            parameter_id: Unique parameter identifier.
            parameter_type: Type of parameter.
            timestamp: Timestamp for the new value.

        Returns:
            Generated value.
        """
        ...

    def reset(self, parameter_id: UUID) -> None:
        """Reset state for a parameter.

        Args:
            parameter_id: Parameter to reset.
        """
        ...


class RealisticTelemetryGenerator:
    """Generates realistic telemetry values with separate state per parameter."""

    def __init__(self, seed: int | None = None) -> None:
        """Initialize generator.

        Args:
            seed: Random seed for reproducibility. If None, uses system randomness.
        """
        self._random = random.Random(seed)
        self._state: dict[UUID, GeneratorState] = {}

    def _get_or_create_state(
        self, parameter_id: UUID, parameter_type: ParameterType
    ) -> GeneratorState:
        """Get existing state or create initial state for a parameter.

        Args:
            parameter_id: Parameter identifier.
            parameter_type: Type of parameter.

        Returns:
            Generator state.
        """
        if parameter_id not in self._state:
            # Initialize with realistic defaults based on type
            initial_value = self._get_initial_value(parameter_type)
            self._state[parameter_id] = GeneratorState(
                current_value=initial_value,
                step_count=0,
                phase=self._random.uniform(0, 2 * math.pi),
            )
        return self._state[parameter_id]

    def _get_initial_value(self, parameter_type: ParameterType) -> float:
        """Get initial value for a parameter type.

        Args:
            parameter_type: Type of parameter.

        Returns:
            Initial value.
        """
        # Realistic initial values
        initial_values = {
            ParameterType.VOLTAGE: 12.5,
            ParameterType.TEMPERATURE: 20.0,
            ParameterType.CURRENT: 2.5,
            ParameterType.PRESSURE: 101.3,
            ParameterType.HUMIDITY: 50.0,
            ParameterType.POWER: 30.0,
            ParameterType.SIGNAL_STRENGTH: -60.0,
        }
        base_value = initial_values.get(parameter_type, 0.0)
        # Add small random variation
        return base_value + self._random.uniform(-0.5, 0.5)

    def generate(
        self,
        parameter_id: UUID,
        parameter_type: ParameterType,
        timestamp: datetime,
    ) -> float:
        """Generate next realistic value for a parameter.

        Args:
            parameter_id: Unique parameter identifier.
            parameter_type: Type of parameter.
            timestamp: Timestamp for the new value.

        Returns:
            Generated value.
        """
        state = self._get_or_create_state(parameter_id, parameter_type)

        # Generate based on parameter type
        if parameter_type == ParameterType.VOLTAGE:
            value = self._generate_voltage(state)
        elif parameter_type == ParameterType.TEMPERATURE:
            value = self._generate_temperature(state, timestamp)
        elif parameter_type == ParameterType.CURRENT:
            value = self._generate_current(state)
        elif parameter_type == ParameterType.PRESSURE:
            value = self._generate_pressure(state)
        elif parameter_type == ParameterType.HUMIDITY:
            value = self._generate_humidity(state)
        elif parameter_type == ParameterType.POWER:
            value = self._generate_power(state)
        elif parameter_type == ParameterType.SIGNAL_STRENGTH:
            value = self._generate_signal_strength(state)
        else:
            value = state.current_value

        # Update state
        state.current_value = value
        state.step_count += 1

        return value

    def _generate_voltage(self, state: GeneratorState) -> float:
        """Generate voltage with random walk and mean reversion.

        Simulates battery voltage oscillating around nominal value.

        Args:
            state: Current state.

        Returns:
            Next voltage value.
        """
        mean = 12.5  # Nominal battery voltage
        reversion_strength = 0.1
        volatility = 0.05

        # Mean reversion: pull towards mean
        drift = reversion_strength * (mean - state.current_value)

        # Random walk component
        noise = self._random.gauss(0, volatility)

        new_value = state.current_value + drift + noise

        # Clamp to realistic bounds
        return max(10.0, min(14.0, new_value))

    def _generate_temperature(
        self, state: GeneratorState, timestamp: datetime
    ) -> float:
        """Generate temperature with diurnal (daily) cycle.

        Simulates day/night temperature variation.

        Args:
            state: Current state.
            timestamp: Current timestamp.

        Returns:
            Next temperature value.
        """
        # Base temperature
        base_temp = 20.0

        # Diurnal cycle (24-hour period)
        hour = timestamp.hour + timestamp.minute / 60.0
        diurnal_amplitude = 10.0  # ±10°C variation
        diurnal_component = diurnal_amplitude * math.sin(
            2 * math.pi * (hour - 6) / 24  # Peak at 2 PM (hour 14)
        )

        # Small random noise
        noise = self._random.gauss(0, 0.5)

        return base_temp + diurnal_component + noise

    def _generate_current(self, state: GeneratorState) -> float:
        """Generate current with random walk and positivity constraint.

        Args:
            state: Current state.

        Returns:
            Next current value.
        """
        mean = 2.5
        reversion_strength = 0.08
        volatility = 0.1

        drift = reversion_strength * (mean - state.current_value)
        noise = self._random.gauss(0, volatility)

        new_value = state.current_value + drift + noise

        # Current must be non-negative
        return max(0.0, min(5.0, new_value))

    def _generate_pressure(self, state: GeneratorState) -> float:
        """Generate pressure with slow drift.

        Simulates atmospheric pressure changes.

        Args:
            state: Current state.

        Returns:
            Next pressure value.
        """
        # Very slow random walk
        drift = self._random.gauss(0, 0.02)
        new_value = state.current_value + drift

        # Atmospheric pressure bounds (kPa)
        return max(95.0, min(105.0, new_value))

    def _generate_humidity(self, state: GeneratorState) -> float:
        """Generate humidity with bounded random walk.

        Args:
            state: Current state.

        Returns:
            Next humidity value (0-100%).
        """
        mean = 50.0
        reversion_strength = 0.05
        volatility = 1.0

        drift = reversion_strength * (mean - state.current_value)
        noise = self._random.gauss(0, volatility)

        new_value = state.current_value + drift + noise

        # Humidity is 0-100%
        return max(0.0, min(100.0, new_value))

    def _generate_power(self, state: GeneratorState) -> float:
        """Generate power with sawtooth pattern.

        Simulates battery charging/discharging cycles.

        Args:
            state: Current state.

        Returns:
            Next power value.
        """
        # Sawtooth: gradual discharge, quick recharge
        cycle_length = 50  # Steps per cycle
        position = state.step_count % cycle_length

        max_power = 50.0
        min_power = 10.0

        if position < 40:
            # Gradual discharge (80% of cycle)
            fraction = position / 40
            base_value = max_power - (max_power - min_power) * fraction
        else:
            # Quick recharge (20% of cycle)
            fraction = (position - 40) / 10
            base_value = min_power + (max_power - min_power) * fraction

        # Add small noise
        noise = self._random.gauss(0, 0.5)

        return max(0.0, base_value + noise)

    def _generate_signal_strength(self, state: GeneratorState) -> float:
        """Generate signal strength with occasional drops.

        Simulates radio signal with intermittent degradation.

        Args:
            state: Current state.

        Returns:
            Next signal strength value (dBm).
        """
        nominal = -60.0  # Good signal strength

        # Random chance of signal drop
        if self._random.random() < 0.05:  # 5% chance of drop
            # Signal degrades
            drop = self._random.uniform(10, 30)
            return nominal - drop

        # Otherwise, hover near nominal with small variations
        noise = self._random.gauss(0, 2.0)
        new_value = nominal + noise

        # Signal strength bounds (dBm)
        return max(-100.0, min(-30.0, new_value))

    def reset(self, parameter_id: UUID) -> None:
        """Reset state for a parameter.

        Args:
            parameter_id: Parameter to reset.
        """
        if parameter_id in self._state:
            del self._state[parameter_id]

    def reset_all(self) -> None:
        """Reset all parameter states."""
        self._state.clear()
