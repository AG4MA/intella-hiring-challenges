"""Telemetry generator engine for backfill and live generation."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.settings import Settings
from app.domain.models import TelemetryData
from app.services.parameter import ParameterService
from app.services.telemetry import TelemetryService
from app.workers.strategies import RealisticTelemetryGenerator

logger = logging.getLogger("telemetry.generator")


def generate_backfill(
    telemetry_service: TelemetryService,
    parameter_service: ParameterService,
    settings: Settings,
) -> int:
    """Generate backfill telemetry data for active parameters.

    Args:
        telemetry_service: Service for creating telemetry points.
        parameter_service: Service for listing parameters.
        settings: Application settings.

    Returns:
        Number of telemetry points generated.
    """
    logger.info(
        "Starting backfill generation for %d hours",
        settings.telemetry_backfill_hours,
    )

    # Get all parameters
    all_parameters = parameter_service.list_all()

    # Filter active parameters
    active_parameters = [p for p in all_parameters if p.is_active]

    if not active_parameters:
        logger.warning("No active parameters found for backfill")
        return 0

    logger.info("Found %d active parameters", len(active_parameters))

    # Calculate time range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=settings.telemetry_backfill_hours)

    # Initialize generator with fixed seed for deterministic backfill
    generator = RealisticTelemetryGenerator(seed=12345)

    # Generate points
    total_points = 0
    current_time = start_time

    while current_time <= end_time:
        for parameter in active_parameters:
            # Generate value
            value = generator.generate(
                parameter.id,
                parameter.parameter_type,
                current_time,
            )

            # Create telemetry point
            try:
                telemetry = TelemetryData(
                    parameter_id=parameter.id,
                    timestamp=current_time,
                    value=value,
                )
                telemetry_service.append_point(telemetry)
                total_points += 1

                logger.debug(
                    "Generated backfill point: parameter=%s, time=%s, value=%.2f",
                    parameter.id,
                    current_time.isoformat(),
                    value,
                )

            except Exception as e:
                logger.warning(
                    "Failed to generate backfill point for parameter %s: %s",
                    parameter.id,
                    str(e),
                )

        # Move to next time step
        current_time += timedelta(seconds=settings.telemetry_step_seconds)

    logger.info("Backfill generation completed: %d points generated", total_points)
    return total_points


async def run_live(
    telemetry_service: TelemetryService,
    parameter_service: ParameterService,
    settings: Settings,
    stop_event: asyncio.Event | None = None,
) -> None:
    """Run live telemetry generation loop.

    Args:
        telemetry_service: Service for creating telemetry points.
        parameter_service: Service for listing parameters.
        settings: Application settings.
        stop_event: Optional event to signal stop. If None, runs forever.
    """
    logger.info(
        "Starting live telemetry generation (interval: %d seconds)",
        settings.telemetry_step_seconds,
    )

    # Initialize generator with no seed for true randomness
    generator = RealisticTelemetryGenerator(seed=None)

    tick_count = 0

    while stop_event is None or not stop_event.is_set():
        tick_count += 1

        # Get current active parameters
        all_parameters = parameter_service.list_all()
        active_parameters = [p for p in all_parameters if p.is_active]

        if not active_parameters:
            logger.warning("No active parameters found for live generation")
        else:
            logger.debug(
                "Live generation tick %d for %d parameters",
                tick_count,
                len(active_parameters),
            )

            current_time = datetime.now(timezone.utc)

            for parameter in active_parameters:
                # Generate value
                value = generator.generate(
                    parameter.id,
                    parameter.parameter_type,
                    current_time,
                )

                # Create telemetry point
                try:
                    telemetry = TelemetryData(
                        parameter_id=parameter.id,
                        timestamp=current_time,
                        value=value,
                    )
                    telemetry_service.append_point(telemetry)

                    logger.debug(
                        "Generated live point: parameter=%s, value=%.2f",
                        parameter.id,
                        value,
                    )

                except Exception as e:
                    logger.warning(
                        "Failed to generate live point for parameter %s: %s",
                        parameter.id,
                        str(e),
                    )

        # Wait for next tick
        await asyncio.sleep(settings.telemetry_step_seconds)

    logger.info("Live telemetry generation stopped after %d ticks", tick_count)
