# Test Suite Documentation

This directory contains all test files and test-related documentation for the PromptYour.AI project.

## 📁 Directory Structure

```
tests/
├── README.md                     # This file - test documentation
├── conftest.py                   # Pytest configuration and fixtures
├── __init__.py                   # Python package initialization
│
├── unit/                         # Unit tests (isolated component testing)
│   ├── backend/                  # Backend unit tests
│   │   ├── __init__.py
│   │   └── test_redesigned_input.py    # Input processing unit tests
│   └── frontend/                 # Frontend unit tests (future)
│       └── __init__.py
│
├── integration/                  # Integration tests (component interaction)
│   ├── backend/                  # Backend integration tests
│   │   ├── __init__.py
│   │   ├── test_lm_studio_integration.py    # LM Studio provider integration
│   │   ├── test_openrouter_integration.py   # OpenRouter provider integration
│   │   ├── test_websocket_chat.py           # WebSocket chat functionality
│   │   └── test_lm_studio_chat.py           # LM Studio via WebSocket
│   └── frontend/                 # Frontend integration tests (future)
│       └── __init__.py
│
├── e2e/                          # End-to-end tests (full system testing)
│   ├── __init__.py
│   ├── test_api.py               # Complete API flow testing
│   └── test_evaluation_system.py # Evaluation system testing
│
├── fixtures/                     # Test data and fixtures
├── data/                         # Test datasets
├── scripts/                      # Test utility scripts
│
└── docs/                         # Test-related documentation
    ├── LM_STUDIO_GUIDE.md        # LM Studio testing guide
    └── TERMINAL_CHAT_GUIDE.md    # Terminal chat testing guide
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Tests individual components in isolation:
- **Input Processing**: `test_redesigned_input.py` - Tests user input processing logic

### Integration Tests (`tests/integration/`)
Tests component interactions and external service integration:
- **LM Studio Integration**: `test_lm_studio_integration.py` - Tests local LLM provider
- **OpenRouter Integration**: `test_openrouter_integration.py` - Tests cloud LLM provider
- **WebSocket Chat**: `test_websocket_chat.py` - Tests real-time chat functionality
- **LM Studio Chat**: `test_lm_studio_chat.py` - Tests LM Studio via WebSocket

### End-to-End Tests (`tests/e2e/`)
Tests complete system functionality:
- **API Flow**: `test_api.py` - Tests complete request processing pipeline
- **Evaluation System**: `test_evaluation_system.py` - Tests model evaluation system

## 🚀 Running Tests

### All Tests
```bash
# From project root
make test
# or
pytest tests/
```

### By Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/
```

### Specific Test Files
```bash
# Run specific test file
pytest tests/integration/backend/test_lm_studio_integration.py

# Run with verbose output
pytest -v tests/integration/backend/test_lm_studio_integration.py

# Run with coverage
pytest --cov=src tests/
```

### Individual Test Scripts
Some tests can also be run as standalone scripts:
```bash
# LM Studio integration test
python tests/integration/backend/test_lm_studio_integration.py

# OpenRouter integration test
python tests/integration/backend/test_openrouter_integration.py

# WebSocket chat test
python tests/integration/backend/test_websocket_chat.py
```

## 🔧 Test Configuration

### Environment Setup
Tests require specific environment variables. Set them in `.env` or export them:

```bash
# For testing
export DATABASE_URL="postgresql://test:test@localhost/test"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="test-jwt-secret-key"
export ENCRYPT_KEY="test-encrypt-key-32-bytes-long12"

# For LM Studio tests
export LM_STUDIO_URL="http://localhost:1234/v1"

# For OpenRouter tests (optional)
export OPENROUTER_API_KEY="your-api-key"
```

### Prerequisites
Different tests require different services to be running:

**Unit Tests**: No external dependencies

**Integration Tests**:
- **LM Studio tests**: Require LM Studio running with a model loaded
- **OpenRouter tests**: Require valid API key (optional, will skip if not available)
- **WebSocket tests**: Require backend server running

**E2E Tests**: Require full backend setup with database and all services

## 📊 Test Coverage

Run tests with coverage reporting:
```bash
# Generate coverage report
pytest --cov=src --cov-report=html tests/

# View coverage in browser
open htmlcov/index.html
```

## 🐛 Debugging Tests

### Enable Debug Output
```bash
# Run with debug logging
pytest -s --log-cli-level=DEBUG tests/

# Run specific test with debugging
pytest -s -v tests/integration/backend/test_lm_studio_integration.py::test_lm_studio_direct
```

### Common Issues

1. **Backend Not Running**: Many integration tests require the backend to be running
   ```bash
   PYTHONPATH=src/backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **LM Studio Not Available**: LM Studio tests will skip if service is not running
   - Start LM Studio and load a model
   - Ensure local server is running on port 1234

3. **Missing API Keys**: Tests requiring API keys will skip if keys are not configured

## 📝 Adding New Tests

### Test Naming Convention
- **Unit tests**: `test_[component_name].py`
- **Integration tests**: `test_[service_name]_integration.py`
- **E2E tests**: `test_[feature_name].py`

### Test Structure
```python
"""
Test description
"""
import pytest
from your_module import YourClass

class TestYourFeature:
    """Test suite for your feature"""
    
    def test_specific_functionality(self):
        """Test specific functionality"""
        # Arrange
        # Act  
        # Assert
        pass
```

### Adding Fixtures
Add reusable test fixtures to `conftest.py`:
```python
@pytest.fixture
def sample_data():
    return {"test": "data"}
```

## 📖 Test Documentation

- **LM Studio Testing**: See `docs/LM_STUDIO_GUIDE.md`
- **Terminal Chat Testing**: See `docs/TERMINAL_CHAT_GUIDE.md`
- **API Testing**: See individual test files for detailed examples

## 🏗️ CI/CD Integration

Tests are designed to run in CI/CD environments:
- Unit tests run on every commit
- Integration tests run on pull requests
- E2E tests run on main branch updates

For CI-friendly execution:
```bash
# Skip tests requiring external services
pytest -m "not integration"

# Run only unit tests in CI
pytest tests/unit/
```