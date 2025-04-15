.PHONY: help install test lint format clean run migrate

help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies and set up pre-commit hooks"
	@echo "  make test         Run tests with pytest"
	@echo "  make coverage     Run tests with coverage report"
	@echo "  make lint         Run linting checks"
	@echo "  make format       Format code"
	@echo "  make clean        Clean up cache and build files"
	@echo "  make run         Start the development server"
	@echo "  make migrate      Run database migrations"

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v

coverage:
	pytest tests/ -v --cov=one_shot_api --cov-report=term-missing --cov-report=html

lint:
	ruff check .

format:
	ruff format .
	ruff check . --fix

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.pyc" -exec rm -rf {} +
	find . -type d -name "*.pyo" -exec rm -rf {} +
	find . -type d -name "*.pyd" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

run:
	uvicorn one_shot_api.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head
