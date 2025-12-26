# Satellite Telemetry API

> **Enterprise-grade FastAPI backend for satellite telemetry management with real-time data generation**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-187%20passed-brightgreen.svg)](#testing)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Domain Model](#domain-model)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Project Structure](#project-structure)
- [Design Decisions](#design-decisions)
- [Performance Considerations](#performance-considerations)
- [Contributing](#contributing)

---

## 🎯 Overview

This is a **production-ready FastAPI application** designed to simulate and manage satellite telemetry systems. Built with clean architecture principles, it provides comprehensive CRUD operations, real-time telemetry data generation, and advanced querying capabilities.

**Key Highlights:**
- ✅ **187 comprehensive tests** with deterministic fixtures
- ✅ **Real-time telemetry generation** with realistic sensor patterns
- ✅ **Clean Architecture** with separated layers (API, Services, Storage, Domain)
- ✅ **Type-safe** with full Pydantic validation and Python type hints
- ✅ **Docker-ready** with health checks and container orchestration
- ✅ **Auto-generated OpenAPI** documentation at `/docs`

### Use Cases

- Satellite operations monitoring and telemetry ingestion
- Time-series data management for IoT/sensor networks
- RESTful API design reference for hierarchical data models
- Educational reference for FastAPI + Clean Architecture

---

## ✨ Features

### Core Functionality

- **Hierarchical Data Model**: Satellite → Unit → Parameter → Telemetry (4-level hierarchy)
- **Full CRUD Operations**: Create, Read, Update, Delete for all entities
- **Advanced Telemetry Querying**: Filter by parameter, time range, with pagination and ordering
- **Operational Status Dashboard**: Real-time aggregated status summary for all satellites
- **Automated Data Generation**: 
  - **Backfill**: 24-hour historical telemetry on startup (~43,000+ data points)
  - **Live Generation**: Continuous real-time telemetry every 10 seconds
- **Realistic Sensor Patterns**: 5 parameter types (voltage, temperature, pressure, battery, signal) with domain-specific variations

### Technical Features

- **Dependency Injection**: Clean separation via FastAPI dependency system
- **Domain Error Handling**: Automatic HTTP status mapping from domain exceptions
- **Request Logging**: Comprehensive middleware for observability
- **Health Checks**: Standard `/health` endpoint for monitoring
- **Environment Configuration**: 12-factor app with `.env` support
- **Code Quality**: Ruff linting + formatting, 100% type-annotated

---

## 🏗️ Architecture

### Layered Architecture (Clean Architecture)

```
┌─────────────────────────────────────────────────────┐
│                    HTTP Layer                       │
│  app/api/  (FastAPI routers, DTOs, middleware)     │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│                  Service Layer                      │
│  app/services/  (Business logic, orchestration)    │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│                 Storage Layer                       │
│  app/storage/  (Repository interfaces, in-memory)  │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│                  Domain Layer                       │
│  app/domain/  (Models, enums, validators, errors)  │
└─────────────────────────────────────────────────────┘
```

**Layer Responsibilities:**

- **API Layer** (`app/api/`): HTTP concerns (routing, validation, serialization)
- **Service Layer** (`app/services/`): Business logic, coordination, transactions
- **Storage Layer** (`app/storage/`): Data access, repositories, persistence abstractions
- **Domain Layer** (`app/domain/`): Core business models, rules, and domain errors

**Cross-Cutting:**
- **Workers** (`app/workers/`): Background tasks (telemetry generator)
- **Core** (`app/core/`): Configuration, settings, shared utilities

---

## 📊 Domain Model

### Entity Relationships

```
Satellite (1) ──┬──> (N) Unit
                │
                └──> Metadata: name, launch_date, status, is_active

Unit (1) ───────┬──> (N) Parameter
                │
                └──> Description, satellite_id (foreign key)

Parameter (1) ──┬──> (N) TelemetryData
                │
                ├──> Attributes: name, unit_of_measurement, parameter_type
                └──> is_active flag

TelemetryData
    ├──> parameter_id (foreign key)
    ├──> timestamp (ISO 8601)
    └──> value (float)
```

### Parameter Types

| Type | Range | Example Use Case |
|------|-------|-----------------|
| `voltage` | 11.0 - 13.0 V | Battery voltage monitoring |
| `temperature` | -20 - 50 °C | Thermal control systems |
| `pressure` | 0.8 - 1.2 bar | Environmental sensors |
| `battery_level` | 0 - 100 % | Power system state of charge |
| `signal_strength` | -90 - -40 dBm | Communication link quality |

### Initial Dataset

**On Startup (Deterministic Seed Data):**
- 1 Satellite: "Intella-Sat-1" (UUID: `00000000-0000-0000-0000-000000000001`)
- 2 Units: "Power System", "Thermal Control"
- 5 Parameters across units (battery_voltage, solar_current, battery_temperature, internal_temp, radiator_temp)
- ~43,000 telemetry points (24-hour backfill at 10-second intervals)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (tested on 3.12)
- **pip** or **uv** for dependency management
- **Docker** (optional, for containerized deployment)

### Local Setup (5 minutes)

1. **Clone the repository:**

```bash
git clone <repository-url>
cd backend
```

2. **Create virtual environment:**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -e ".[dev]"
```

4. **Run the application:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API:**

- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

### Base URL: `/v1`

### Satellites

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/satellites/` | List all satellites (paginated) |
| `GET` | `/v1/satellites/{id}` | Get satellite by ID |
| `PUT` | `/v1/satellites/{id}` | Update satellite metadata |
| `PUT` | `/v1/satellites/{id}/activate` | Activate a satellite |
| `PUT` | `/v1/satellites/{id}/disable` | Disable a satellite (soft delete) |
| `GET` | `/v1/satellites/status` | **Operational status summary** (aggregated metrics) |

### Units

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/units/` | List all units with optional satellite filter |
| `GET` | `/v1/units/{id}` | Get unit by ID |
| `POST` | `/v1/units/` | Create new unit for a satellite |
| `PUT` | `/v1/units/{id}` | Update unit details |
| `DELETE` | `/v1/units/{id}` | Delete unit (cascade deletes parameters) |

### Parameters

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/parameters/` | List parameters with optional unit filter |
| `GET` | `/v1/parameters/{id}` | Get parameter by ID |
| `POST` | `/v1/parameters/` | Create new parameter for a unit |
| `PUT` | `/v1/parameters/{id}` | Update parameter configuration |
| `DELETE` | `/v1/parameters/{id}` | Delete parameter (cascade deletes telemetry) |

### Telemetry

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/telemetry/` | **Query telemetry** with filters (see below) |

**Query Parameters for `/v1/telemetry/`:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `parameter_id` | UUID | **(Required)** Filter by parameter | `?parameter_id=<uuid>` |
| `from_ts` | DateTime | Start time (ISO 8601, inclusive) | `?from_ts=2025-12-26T00:00:00Z` |
| `to_ts` | DateTime | End time (ISO 8601, inclusive) | `?to_ts=2025-12-26T23:59:59Z` |
| `order` | Enum | Sort order: `asc` or `desc` (default: `desc`) | `?order=asc` |
| `limit` | Integer | Max records (1-10000, default: 100) | `?limit=500` |
| `offset` | Integer | Pagination offset (default: 0) | `?offset=100` |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (returns `{"status": "ok"}`) |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application Environment
ENVIRONMENT=dev             # dev, staging, prod
DEBUG=false                 # Enable debug mode

# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Telemetry Generation
TELEMETRY_STEP_SECONDS=10   # Interval between live telemetry points
TELEMETRY_BACKFILL_HOURS=24 # Historical data window on startup
```

**Defaults** (if `.env` not provided):
- `ENVIRONMENT=dev`
- `LOG_LEVEL=INFO`
- `TELEMETRY_STEP_SECONDS=10`
- `TELEMETRY_BACKFILL_HOURS=24`

---

## 💻 Development

### Code Quality Tools

```bash
# Lint check
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code
ruff format .
```

### Running the Development Server

```bash
# With auto-reload on file changes
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With custom log level
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

---

## 🧪 Testing

### Test Suite Overview

- **Total Tests**: 187 passed, 3 skipped
- **Coverage Areas**: API, Services, Storage, Domain, Workers, Integration
- **Frameworks**: `pytest`, `httpx` (TestClient)

### Running Tests

```bash
# Run all tests
pytest

# Run with quiet mode
pytest -q

# Run specific test file
pytest tests/api/test_satellites_api.py

# Run integration tests only
pytest tests/integration/ -v
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and run
docker compose up --build

# Run in detached mode
docker compose up -d

# Stop services
docker compose down
```

**Access the application:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 🧠 Design Decisions

### 1. In-Memory Storage

**Decision**: Use in-memory dictionaries for data persistence.

**Rationale**:
- ✅ Simplifies local development and testing
- ✅ Eliminates database setup overhead
- ✅ Enables deterministic test fixtures
- ❌ Data lost on restart (acceptable for demo)

**Migration Path**: Repository interfaces make it trivial to swap for PostgreSQL/TimescaleDB.

### 2. Background Telemetry Generation

**Decision**: Run backfill + live generation as async background tasks.

**Implementation**:
- Backfill runs once on startup (24-hour history, ~43K points)
- Live generator runs continuously every 10 seconds
- Graceful shutdown cancels tasks

### 3. Clean Architecture Layering

**Decision**: Strict separation into API, Service, Storage, Domain layers.

**Benefits**:
- Business logic independent of HTTP framework
- Easy to test (mock repositories, no HTTP required)
- Domain models remain pure (no FastAPI dependencies)

---

## ⚡ Performance Considerations

### Current Performance Metrics

- Startup time: ~2-3 seconds (includes 43K point backfill)
- Status aggregation: <10ms for 43K points (in-memory)
- Telemetry query (1000 points): <5ms

### Optimization for Production

1. **Indexing**: Add indexes on `satellite_id`, `unit_id`, `parameter_id`, `timestamp`
2. **Time-Series DB**: Use TimescaleDB or InfluxDB for telemetry
3. **Caching**: Add Redis for status summary (expensive aggregation)
4. **Batch Inserts**: Use bulk insert for telemetry generation (100x faster)

---

## 🎯 Summary

This API demonstrates:
- ✅ **Enterprise-grade architecture** with clean separation of concerns
- ✅ **Comprehensive testing** with 187 deterministic tests
- ✅ **Real-time data generation** with realistic sensor patterns
- ✅ **Production-ready tooling** (Docker, Makefile, health checks)
- ✅ **API best practices** (pagination, filtering, error handling)
- ✅ **Type safety** with Pydantic and full type annotations

**Built for scalability**: Repository interfaces make it trivial to migrate from in-memory to PostgreSQL/TimescaleDB for production deployment.

---

**Version**: 1.0.0  
**Last Updated**: December 26, 2025
