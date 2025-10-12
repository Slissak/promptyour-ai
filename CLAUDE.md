# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ GIT WORKFLOW - CRITICAL RULES

**NEVER WORK DIRECTLY ON MAIN BRANCH!**

### Branching Strategy

**For ANY code changes (features, fixes, improvements):**

1. **Create a feature branch** from main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/descriptive-name
   # or: git checkout -b fix/bug-description
   ```

2. **Make changes on the branch** (not main)

3. **Commit changes** to the branch:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

4. **Push branch** to remote:
   ```bash
   git push origin feature/descriptive-name
   ```

5. **Ask user** before merging to main or creating pull requests

### Branch Naming Conventions

- `feature/` - New features (e.g., `feature/add-user-authentication`)
- `fix/` - Bug fixes (e.g., `fix/response-timeout`)
- `refactor/` - Code refactoring (e.g., `refactor/api-client`)
- `docs/` - Documentation updates (e.g., `docs/update-readme`)
- `test/` - Test additions (e.g., `test/mobile-frontend`)

### When to Work on Main

**ONLY for:**
- Documentation-only updates (README, CLAUDE.md)
- Minor typo fixes in documentation
- Configuration file updates (when explicitly requested)

**ALWAYS ASK FIRST** before committing to main!

---

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

### Git Commands (Feature Branch Workflow)

**Starting new work:**
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

**During development:**
```bash
git status                    # Check what's changed
git add <files>               # Stage specific files
git commit -m "message"       # Commit changes
git push origin feature/your-feature-name  # Push to remote
```

**Checking branch status:**
```bash
git branch                    # List local branches
git branch -a                 # List all branches (local + remote)
git log --oneline -10         # Recent commits
```

**Switching branches:**
```bash
git checkout main             # Switch to main
git checkout feature/name     # Switch to feature branch
```

## Development Standards

### Code Quality
- Code formatting with Black (88 character line length)
- Type checking with MyPy (strict mode enabled)
- Linting with flake8
- Testing with pytest (with coverage reporting)
- Python 3.8+ compatibility required

### Git Standards
- **NEVER commit directly to main** (use feature branches)
- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Push branches to remote for backup
- Ask user before merging to main or creating PRs

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
- **Optional enhanced configuration** - user can select any, all, or no parameters
- **Build-time config generation** - YAML → TypeScript pipeline with type safety
- **Conversation state management** - preferences remembered within conversation
- **Session-based history** - clean isolation per conversation, no cross-chat leakage
- Multi-language support (English, Arabic, Hebrew with RTL)
- Real-time WebSocket communication with REST fallback

### Development Tooling
- UV package manager for fast Python dependency resolution
- Comprehensive test coverage across all layers
- Evaluation framework for metrics and benchmarking
- Black code formatting (88 char line length)
- MyPy type checking (strict mode)
- Flake8 linting

## Current Status (October 12, 2025)

### Recently Completed Features (October 12, 2025)
- ✅ **Enhanced Response Configuration System**
  - Optional theme/audience/response_style parameters (user can select any combination)
  - Smart defaults applied when parameters not provided
  - First enhanced request shows all options, subsequent requests show only additional context
  - Conversation state management (preferences remembered within conversation)

- ✅ **Build-Time Configuration Generation**
  - Industry-standard YAML → TypeScript generation pipeline
  - Auto-generates on `npm run dev` and `npm run build`
  - Single source of truth (config/ YAML files)
  - Type-safe with const assertions

- ✅ **Conversation History Isolation**
  - Fixed critical bug where system prompt showed history from multiple chats
  - Current question no longer included in message_history
  - Session-based conversations (no localStorage persistence)
  - Complete history wipe on new chat or page reload

- ✅ **UI Size Reduction**
  - Enhanced configuration window reduced to ~1/3 of original size
  - More compact while maintaining readability

### Previously Completed Features
- ✅ Backend API with three-tier chat system (Quick/Enhanced/Raw)
- ✅ Web frontend (Next.js 15) with full i18n support (EN/AR/HE with RTL)
- ✅ Mobile frontend (Expo SDK 52) with Zustand, Expo Router, and WebSocket support
- ✅ Shared TypeScript library for cross-platform code reuse
- ✅ Terminal chat interface with debug mode and RAW comparison
- ✅ Multiple AI provider integrations (OpenRouter, Anthropic, Groq, LM Studio)
- ✅ Centralized configuration system (config/ YAML files)
- ✅ Extended thinking/reasoning support for thinking-capable models
- ✅ Free NVIDIA Nemotron Nano 9B model for quick responses

### Active Development
- 🔄 Add comprehensive tests for mobile frontend
- 🔄 Refactor mobile frontend to use shared library (optional optimization)
- 🔄 Production deployment configuration
- 🔄 Database persistence implementation