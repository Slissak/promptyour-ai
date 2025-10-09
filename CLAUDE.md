# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

"promp_your_ai" is a cross-platform AI chat application with a FastAPI backend and multiple frontend implementations (Web, Mobile, Terminal). The project features a two-tier chat system with intelligent model routing, theme-based responses, and audience targeting.

## Project Architecture

### Directory Structure
- `src/backend/` - FastAPI backend with WebSocket support, API routes, models, services, and AI provider integrations
- `src/web-frontend/` - Next.js 15 web application with i18n and responsive design
- `src/mobile-frontend/` - React Native/Expo mobile app (Expo SDK 52) with Zustand state management and Expo Router
- `src/shared/` - Shared TypeScript API client library for cross-platform code reuse
- `src/frontend/` - Legacy frontend implementation
- `tests/` - Comprehensive test suite with unit, integration, and e2e tests
- `evaluations/` - Evaluation framework with metrics, benchmarks, and reporting
- `docs/` - Documentation files
- `scripts/` - Utility scripts
- `data/` - Data files and datasets
- `config/` - Configuration files

## Development Commands

### Environment Setup
```bash
# Backend setup
uv venv .venv
source .venv/bin/activate
make install-dev

# Web frontend setup
cd src/web-frontend
npm install

# Mobile frontend setup
cd src/mobile-frontend
npm install
```

### Running Applications

**Backend** (Port 8001):
```bash
make run-backend
# or: PYTHONPATH=src/backend python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Web Frontend** (Port 3000):
```bash
cd src/web-frontend
npm run dev
```

**Mobile Frontend**:
```bash
cd src/mobile-frontend
npm start        # Expo Dev Server
npm run web      # Web version
npm run ios      # iOS Simulator
npm run android  # Android Emulator
```

**Terminal Chat**:
```bash
python terminal_chat.py --api http://localhost:8001 --quick  # Quick mode
python terminal_chat.py --api http://localhost:8001          # Full mode
```

### Testing Commands
- `make test` - Run all backend tests with coverage
- `make test-unit` - Run unit tests only (tests/unit/)
- `make test-integration` - Run integration tests only (tests/integration/)
- `make test-e2e` - Run end-to-end tests only (tests/e2e/)
- Individual test files can be run from tests/ directory

### Other Development Tasks
- `make lint` - Run flake8 linting on backend
- `make format` - Format backend code with black
- `make type-check` - Run mypy type checking on backend
- `make run-eval` - Run evaluations and benchmarks
- `make clean` - Remove generated files and caches

## Development Standards

- Code formatting with Black (88 character line length)
- Type checking with MyPy (strict mode enabled)
- Linting with flake8
- Testing with pytest (with coverage reporting)
- Python 3.8+ compatibility required

## Architecture Notes

### Backend
- FastAPI framework with WebSocket and REST API support
- Two-tier chat system: Quick (one-liner), Enhanced (detailed), Raw (unprocessed) modes
- Multiple AI provider integrations: OpenAI, Anthropic, Groq, OpenRouter, LM Studio
- Centralized configuration system (src/backend/app/config/settings.py)
- Extended thinking/reasoning support for thinking-capable models
- Internal reasoning storage without user display

### Frontend
- **Web**: Next.js 15 with TypeScript, Tailwind CSS, next-intl for i18n, RTL support
- **Mobile**: Expo SDK 52, React Native, Zustand state management, Expo Router, comprehensive features
- **Shared Library**: TypeScript API client with 95% code reuse across platforms
- **Terminal**: Python-based CLI with rich formatting

### Key Features
- Theme-based responses (9 themes: coding, creative, business, etc.)
- Audience targeting (6 levels: kids to experts)
- Response style customization (brief, detailed, instructions, comprehensive)
- Multi-language support (English, Arabic, Hebrew with RTL)
- Conversation history persistence
- Real-time WebSocket communication with REST fallback

### Development Tooling
- UV package manager for fast Python dependency resolution
- Comprehensive test coverage across all layers
- Evaluation framework for metrics and benchmarking
- Black code formatting (88 char line length)
- MyPy type checking (strict mode)
- Flake8 linting

## Current Status (October 2025)

### Completed
- ✅ Backend API with two-tier chat system
- ✅ Web frontend (Next.js) with full i18n support
- ✅ Mobile frontend (Expo SDK 52) with Zustand, Expo Router, and WebSocket support
- ✅ Shared TypeScript library for cross-platform support
- ✅ Terminal chat interface
- ✅ Multiple AI provider integrations
- ✅ Centralized configuration system
- ✅ Extended thinking/reasoning support

### Pending
- ⚠️ Commit backend changes (lm_studio_provider.py, schemas.py)
- ⚠️ Commit new mobile frontend files
- 🔄 Add tests for mobile frontend
- 🔄 Refactor mobile frontend to use shared library (optional optimization)
- 🔄 Production deployment configuration