# Minimal Dockerfile for FastAPI app (non-root user)

FROM python:3.12-slim

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./

RUN python -m pip install --upgrade pip

# Copy app source
COPY . /app

# Install package with dev dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Ensure the non-root user owns the code
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
