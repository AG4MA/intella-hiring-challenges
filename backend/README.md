# Backend API

FastAPI backend service with centralized configuration, standard logging, and health check.

## Prerequisites

- Python 3.10+
- pip

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -e ".[dev]"
```

4. (Optional) Create a `.env` file for configuration:

```env
ENVIRONMENT=dev
DEBUG=false
LOG_LEVEL=INFO
TELEMETRY_STEP_SECONDS=10
TELEMETRY_BACKFILL_HOURS=24
```

## Run

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Test

Run the test suite:

```bash
pytest -q
```

## Ruff (Linting & Formatting)

Check code style:

```bash
ruff check .
```

Format code:

```bash
ruff format .
```

## Endpoints

| Method | Path      | Description         |
|--------|-----------|---------------------|
| GET    | `/health` | Health check        |
