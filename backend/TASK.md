# Intella Backend Engineer Assessment

**Project:** Satellite Telemetry API

## Context

At Intella, we build AI-powered software for satellite operations. A fundamental capability is ingesting, storing, and exposing satellite telemetry data through well-designed APIs.

Your task is to build a **minimal but well-architected FastAPI application** that simulates a satellite telemetry system with CRUD capabilities. This assessment evaluates your ability to:

- Design RESTful APIs following industry best practices
- Model complex domain relationships
- Write clean, maintainable Python code
- Make architectural decisions that balance simplicity with extensibility

## Domain Model

The system manages a hierarchical structure of satellite components and their telemetry data

```
Satellite (e.g., "Intella-Sat-1")
└── Unit (sensor group, e.g., "Power System", "Thermal Control")
    └── Parameter (individual sensor: voltage, temperature, pressure, etc.)
        └── Telemetry Data Points (timestamp, value)
```

**Example Structure:**

```
Satellite: Intella-Sat-1
├── Unit: Power System
│   ├── Parameter: battery_voltage (telemetry: 12.4V, 12.5V, 12.3V...)
│   ├── Parameter: solar_current (telemetry: 2.1A, 2.3A, 2.2A...)
│   └── Parameter: battery_temperature (telemetry: 21°C, 22°C, 21.5°C...)
└── Unit: Thermal Control
    ├── Parameter: internal_temp (telemetry: 18°C, 19°C, 18.5°C...)
    └── Parameter: radiator_temp (telemetry: -10°C, -9°C, -11°C...)
```

## Requirements

### 1. Data Generation

Implement a telemetry data generator that simulates realistic satellite sensor readings:

- **Time-series generation**: Create data points with timestamps at regular intervals (e.g., every 10 seconds)
- **Parameter types**: Support at least 3-5 different parameter types:
  - `voltage` (e.g., 11.5-13.0V with small variations)
  - `temperature` (e.g., -20°C to 50°C)
  - `pressure` (e.g., 0.8-1.2 bar)
  - `battery_level` (e.g., 0-100%)
  - `signal_strength` (e.g., -90 to -40 dBm)
- **Realistic patterns**: Values should have realistic variations (not random noise)
- **Storage**: Data must be stored in-memory or in the disk with a file format. You can also use a db if you want but be careful on the time consumption.
- **Initial data**: Generate historical telemetry for at least the past 24 hours

### 2. Data Model

Design and implement a clear domain model using Pydantic:

- **Hierarchy**: Satellite → Unit → Parameter → Telemetry Data
- **Minimum data**:
  - 1 satellite with a unique ID and name
  - 2 units per satellite (e.g., "Power System", "Thermal Control")
  - 3-5 parameters per unit
- **Pydantic models**: Create models for:
  - `Satellite` (id, name, units, metadata like launch_date, status)
  - `Unit` (id, name, satellite_id, parameters, description)
  - `Parameter` (id, name, unit_id, unit_of_measurement, parameter_type)
  - `TelemetryData` (id, parameter_id, timestamp, value)
- **Validation**: Use Pydantic validators for data integrity (e.g., value ranges, timestamp formats)

### 3. REST API (FastAPI) - CRUD Operations

Implement a FastAPI REST API layer with CRUD capabilities:

- List all satellites with pagination support
- Get detailed satellite information
- List all units for a satellite
- Get specific unit and parameter details
- Create, update and delete a new unit for a satellite
- Create, update and delete a new parameter for a satellite
- Activate a new satellite (It's not possible to create a satellite from scratch)
- Update satellite information
- Disable a satellite (Don't delete it from the database, just deactivate)
- Query telemetry data with filters to retrieve the data (unit, parameters, start_time, end_time)
— API health check
— Get satellite operational status summary

### 4. Code Quality Standards

Your code must demonstrate professional software engineering practices:

- **PEP 8**: Follow Python style guide (use `black` or `ruff` for formatting)
- **PEP 257**: Include comprehensive docstrings for all modules, classes, and functions
- **Type Hints (PEP 484)**: Use type annotations throughout the codebase
- **Project Structure**: Organize code into logical modules
- **Ruff Configuration**: A pre-configured `pyproject.toml` with ruff settings is provided in the repository
  - Your code must comply with these standards
  - Check compliance: `ruff check .`
  - Format your code: `ruff format .`

### 5. Documentation

Provide comprehensive documentation for users and developers:

- **Project README.md** must include:
  - Project overview and objectives
  - Prerequisites (Python version, dependencies)
  - Installation instructions (step-by-step)
  - How to run the application
  - Other documentation regarding design choices
  
- **API Documentation**:
  - FastAPI auto-generates Swagger UI at `/docs`
  - Ensure all endpoints have clear descriptions
  - Add request/response examples in docstrings
  - Document query parameters and their effects

- **Architecture Documentation** (optional):
  - If you have significant architectural decisions or trade-offs to explain, you may document them in a separate file (e.g., `ARCHITECTURE.md`)
  - This is not required but can be useful for complex design choices

### 6. Testing

Implement test coverage for your application:

- **Unit tests** for services and generators
- **Integration tests** for API endpoints
- Use `pytest` with fixtures
- Aim for reasonable code coverage
- Tests should cover:
  - Core API functionality
  - Data validation
  - Error handling scenarios
  - Edge cases

### 7. Version Control Best Practices

Demonstrate professional Git workflow:

- **Repository Setup**:
  - Fork the `intella-hiring-challenges` repository
  - Add the Intella evaluators as contributors to the repository
  - Work within your forked repository
  - You have freedom to organize your Git workflow as you prefer (remember to commit frequently)
  - When ready to submit, ensure your forked repository is accessible (public or add reviewers as collaborators)
  
- **Commit Strategy** (optional but recommended):
  - Write clear commit messages following conventions:
    - `feat: add satellite CRUD endpoints`
    - `refactor: extract telemetry generator to service layer`
    - `docs: update README with API examples`
    - `fix: correct timestamp validation in telemetry model`
  
- **Branch Strategy** (optional):
  - Work on feature branches if comfortable
  - Use meaningful branch names: `feature/telemetry-endpoints`, `refactor/data-models`
  
- **Completion**:
  - Invite reviewers: [emails will be provided]
  - Ensure all code is pushed and documented

## Bonus Requirements (Optional)

Pick any of these to showcase additional skills:

- [ ] **Docker**: Add `Dockerfile` and `docker-compose.yml` for containerized execution
  - Single command setup: `docker-compose up`
  - Include environment configuration
  
- [ ] **Authentication**: Implement API security layer
  - Simple API key authentication, or
  - JWT-based authentication with login endpoint
  
- [ ] **Extended Data**: Scale up the data model
  - Add 2-3 more satellites with different unit configurations
  - Demonstrate variety in parameter types
  
- [ ] **Makefile**: Provide convenient command shortcuts
  - `make install` - Install dependencies
  - `make run` - Start the application
  - `make test` - Run tests
  - `make lint` - Run code quality checks
  - `make format` - Format code with black/ruff
  
- [ ] **Configuration Management**: Use `pydantic-settings`
  - Support `.env` file for configuration
  - Allow environment-based settings (dev/prod)
  
- [ ] **Modern Package Manager**: Use `uv`, `poetry`, or `pdm` instead of pip
  - Better dependency management
  - Reproducible builds
  
- [ ] **Logging**: Implement structured logging
  - Use `structlog` or Python's `logging` module
  - Log levels: DEBUG, INFO, WARNING, ERROR
  - Include request IDs for tracing
  
- [ ] **Database**: Replace in-memory storage with SQLite or PostgreSQL
  - Use SQLAlchemy ORM
  - Maintain the same API interface
  
- [ ] **API Versioning**: Implement `/v1/` prefix for API routes
  - Prepare for future API evolution

## Nice to Have

- **Commit History**: Making frequent, atomic commits that show your development process can be helpful for reviewers, but you have complete freedom to organize your Git workflow as you prefer

## Evaluation Criteria

Your submission will be evaluated across multiple dimensions:

| Area | What We Look For | Weight |
|------|------------------|--------|
| **Architecture** | Clear separation of concerns, sensible module structure, scalability considerations | ⭐⭐⭐⭐⭐ |
| **Code Quality** | Readability, consistency, proper use of Python idioms, type safety | ⭐⭐⭐⭐⭐ |
| **API Design** | RESTful conventions, proper HTTP status codes, meaningful responses, error handling | ⭐⭐⭐⭐⭐ |
| **Error Handling** | Graceful handling of edge cases, validation errors, proper status codes | ⭐⭐⭐⭐⭐ |
| **Documentation** | Clear README, code comments, API documentation | ⭐⭐⭐⭐ |
| **Testing** | Comprehensive unit/integration tests, edge case coverage | ⭐⭐⭐⭐ |
| **Domain Understanding** | Appropriate modeling of satellite/unit/parameter hierarchy, realistic telemetry | ⭐⭐⭐ |
| **Tooling** | Effective use of modern Python ecosystem (FastAPI, Pydantic, etc.) | ⭐⭐⭐ |
| **Git Workflow** | Commit history that tells a story of iterative development (nice to have) | ⭐⭐⭐ |

### Key Evaluation Questions

We'll be asking ourselves:

1. **Can we run the project easily?** Clear setup instructions, minimal friction
2. **Is the code maintainable?** Could another engineer easily extend this?
3. **Does the API make sense?** Intuitive endpoints, predictable behavior
4. **Did they make good trade-offs?** Balance between simplicity and completeness
5. **Do they understand the domain?** Satellite telemetry modeling makes sense
6. **Can they work with modern tools?** FastAPI, Pydantic, type hints used effectively
7. **Do they think about edge cases?** Error handling, validation, boundaries
8. **Is their Git history informative?** Commits show thoughtful progression

## Time Expectation

**Estimated time**: Maximum 8 hours

**Our advice**: Focus on **quality over quantity**. A smaller, well-crafted solution is significantly better than a large, messy one.

### Suggested Breakdown

- **Hours 1-2**: Project setup, domain modeling, basic structure
- **Hours 3-4**: Data generator and storage implementation
- **Hours 5-6**: Core API endpoints with full CRUD operations
- **Hour 7**: Testing implementation (unit and integration tests)
- **Hour 8**: Documentation, refinement, and final polish

## Expected Deliverables

Your final submission should include:

### 1. Working Application

- FastAPI server that starts without errors
- All mandatory endpoints functional
- Swagger UI accessible at `/docs`

### 2. Source Code

- Well-organized project structure
- Type-annotated Python code
- Pydantic models for all entities
- Clean, well-structured code

### 3. Documentation

- **README.md** with:
  - Project description
  - Setup instructions
  - How to run the application
  - API usage examples
  - Architecture overview (or in separate ARCHITECTURE.md if preferred)
- API documentation via Swagger UI

### 4. Git History

- Clear commit messages (recommended but not required)
- Your preferred Git workflow

## Submission Process

1. **Add reviewers as collaborators**
   - Go to Settings → Collaborators
   - Add the provided reviewer accounts
   - Ensure they have Read access minimum

2. **Finalize your code**
   - Ensure all features work as expected
   - Run a final test of all endpoints
   - Clean up any debug code or TODOs

3. **Update documentation**
   - Verify README is complete and accurate
   - Test setup instructions on a clean environment
   - Add any final notes or considerations

4. **Push to repository**
   - Commit any final changes
   - Push all branches to your remote repository
   - Verify everything is visible on GitHub

5. **Notify us**
   - Reply to the email with your repository link
   - Confirm submission is ready for review
   - Include any special notes or highlights

## Tips for Success

- **Start simple**: Get a basic version working first, then enhance
- **Test as you go**: Use `/docs` to manually test each endpoint
- **Commit frequently**: Don't wait until the end to commit
- **Read error messages**: FastAPI provides excellent error feedback
- **Use AI tools**: They're allowed and encouraged - but review the code
- **Ask questions**: If requirements are unclear, make reasonable assumptions and document them
- **Time-box yourself**: Don't spend hours on a single feature
- **Focus on fundamentals**: Architecture and code quality matter most

## FAQ

**Q: Can I use a database instead of in-memory storage?**  
A: Yes, that's a bonus requirement. But in-memory is perfectly fine for the core assessment.

**Q: How realistic should the telemetry data be?**  
A: It should have logical patterns (e.g., temperature doesn't jump randomly between -50°C and 100°C), but complex physical modeling isn't necessary.

**Q: Should I implement authentication?**  
A: It's optional (bonus). Focus on core features first.

**Q: Can I use libraries beyond FastAPI and Pydantic?**  
A: Yes, use whatever makes sense. Document your choices.

**Q: What Python version should I target?**  
A: Python 3.10+ is recommended. Specify in your README.

**Q: Should I deploy this somewhere?**  
A: Not required. Local execution is fine.

**Q: How detailed should my commits be?**  
A: Meaningful messages that explain what and why. Avoid "update" or "fix stuff".

**Q: Can I look at the FastAPI documentation?**  
A: Absolutely! Use all resources available to you.

---

## Final Note

This assessment is designed to be challenging but achievable. We're not looking for perfection—we want to see how you approach problems, structure solutions, and write code that others can work with.

**Remember**: At Intella, we value engineers who can:

- Create something that has a value, it's simple and it's working
- Build reliable systems
- Write maintainable code
- Make pragmatic decisions
- Learn and adapt quickly
- Communicate clearly through code and documentation

Good luck! We're excited to see what you build. 🚀
