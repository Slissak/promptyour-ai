"""Pytest configuration and shared fixtures."""

import os
import sys
from pathlib import Path

# Add the backend source directory to Python path for imports
project_root = Path(__file__).parent.parent
backend_src = project_root / "src" / "backend"
sys.path.insert(0, str(backend_src))

# Set default test environment variables
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost/test')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379')
os.environ.setdefault('JWT_SECRET', 'test-jwt-secret-key')
os.environ.setdefault('ENCRYPT_KEY', 'test-encrypt-key-32-bytes-long12')
os.environ.setdefault('LM_STUDIO_URL', 'http://localhost:1234/v1')

import pytest


@pytest.fixture
def sample_fixture():
    """Sample fixture for testing."""
    return "test_data"