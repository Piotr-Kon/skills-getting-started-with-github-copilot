"""
Pytest configuration and shared fixtures for testing the FastAPI application.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that resets the in-memory activities database before and after each test.
    This ensures database isolation between tests.
    
    Uses a deep copy of the original activities to preserve the test database state.
    """
    # Store original state
    original_activities = deepcopy(activities)
    
    # Yield to run the test
    yield
    
    # Restore original state after test completes (teardown)
    activities.clear()
    activities.update(original_activities)
