# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

"promp_your_ai" is a Python project with a well-structured architecture including frontend, backend, tests, and evaluations components. The project uses UV for dependency management and includes comprehensive development tooling.

## Project Architecture

### Directory Structure
- `src/backend/` - Backend application with API routes, models, services, and utilities
- `src/frontend/` - Frontend application with components, pages, templates, and static assets  
- `tests/` - Comprehensive test suite with unit, integration, and e2e tests
- `evaluations/` - Evaluation framework with metrics, benchmarks, and reporting
- `docs/` - Documentation files
- `scripts/` - Utility scripts
- `data/` - Data files and datasets
- `config/` - Configuration files

## Development Commands

### Environment Setup
```bash
# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
make install-dev
```

### Testing Commands
- `make test` - Run all tests with coverage
- `make test-unit` - Run unit tests only (tests/unit/)
- `make test-integration` - Run integration tests only (tests/integration/)
- `make test-e2e` - Run end-to-end tests only (tests/e2e/)
- Individual test files can be run from tests/ directory

### Other Development Tasks
- `make lint` - Run flake8 linting
- `make format` - Format code with black
- `make type-check` - Run mypy type checking

### Application Running
- `make run-backend` - Start backend application
- `make run-frontend` - Start frontend application  
- `make run-eval` - Run evaluations and benchmarks

### Cleanup
- `make clean` - Remove generated files and caches

## Development Standards

- Code formatting with Black (88 character line length)
- Type checking with MyPy (strict mode enabled)
- Linting with flake8
- Testing with pytest (with coverage reporting)
- Python 3.8+ compatibility required

## Architecture Notes

- Backend uses FastAPI framework patterns
- Frontend includes component-based architecture
- Comprehensive test coverage across all layers
- Evaluation framework for metrics and benchmarking
- UV package manager for fast dependency resolution