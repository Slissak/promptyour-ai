.PHONY: help install install-dev test lint format type-check run-backend run-frontend run-eval clean

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@egrep '^(.+)\s*:.*?## (.+)' $(MAKEFILE_LIST) | column -t -c 2 -s ':#'

install:  ## Install production dependencies
	uv pip install -r requirements.txt

install-dev:  ## Install development dependencies
	uv pip install -r requirements.txt
	uv pip install -e ".[dev]"

test:  ## Run tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit:  ## Run unit tests only
	pytest tests/unit/ -v

test-integration:  ## Run integration tests only
	pytest tests/integration/ -v

test-e2e:  ## Run end-to-end tests only
	pytest tests/e2e/ -v

lint:  ## Run linting
	flake8 src/ tests/ evaluations/

format:  ## Format code
	black src/ tests/ evaluations/

type-check:  ## Run type checking
	mypy src/

run-backend:  ## Run backend application
	python -m src.backend.main

run-frontend:  ## Run frontend application
	python -m src.frontend.app

run-eval:  ## Run evaluations
	python -m evaluations.run_evaluations

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf build/ dist/ *.egg-info/