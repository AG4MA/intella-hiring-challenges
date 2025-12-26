PYTHON ?= python
PIP ?= $(PYTHON) -m pip
RUFF ?= $(PYTHON) -m ruff
PYTEST ?= $(PYTHON) -m pytest
UVI = uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: install run test lint format docker-up clean

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e '.[dev]'

run:
	$(UVI)

test:
	$(PYTEST) tests/ -q

lint:
	$(RUFF) check . --fix || true

format:
	$(RUFF) format .

docker-up:
	docker-compose up --build

clean:
	rm -rf .pytest_cache .ruff_cache
