"""
Request logging middleware.

Provides observability by logging all HTTP requests with:
- Unique request ID (UUID)
- HTTP method
- Request path
- Response status code
- Request duration in milliseconds
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all incoming HTTP requests.

    Adds a unique request ID to each request and logs:
    - request_id: UUID for tracing
    - method: HTTP method (GET, POST, etc.)
    - path: Request path
    - status: HTTP status code
    - duration_ms: Request duration in milliseconds
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log details."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store request ID in request state for potential use in handlers
        request.state.request_id = request_id

        # Record start time
        start_time = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log request details
        logger.info(
            "request_id=%s method=%s path=%s status=%d duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        # Add request ID to response headers for client tracing
        response.headers["X-Request-ID"] = request_id

        return response
