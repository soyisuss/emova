import pytest
import numpy as np
from fastapi.testclient import TestClient

# Mock the database before importing the app
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def mock_db_connection():
    """Mock MongoDB connection to avoid connecting to real DB during tests."""
    from unittest.mock import MagicMock, AsyncMock
    mock_db = MagicMock()
    
    collections_cache = {}
    def get_collection(name):
        if name not in collections_cache:
            collections_cache[name] = AsyncMock()
        return collections_cache[name]
        
    mock_db.__getitem__ = MagicMock(side_effect=get_collection)
    yield mock_db

@pytest.fixture
def mock_user():
    from emova.api.models.user import UserInDB
    from bson import ObjectId
    return UserInDB(
        id=ObjectId(),
        email="test@example.com",
        firstName="Test",
        lastName="User",
        passwordHash="hashed",
        createdAt="2026-01-01T00:00:00Z"
    )

@pytest.fixture
def api_client(mock_db_connection, mock_user):
    """Returns a TestClient instance for the FastAPI application with mocked user auth."""
    from emova.api.main import app
    from emova.api.routers.auth import get_current_user
    from emova.api.db.database import get_database
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_database] = lambda: mock_db_connection
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def dummy_image_rgb():
    """Returns a dummy 224x224 RGB image (numpy array)."""
    # Create a 300x300 white image (BGR format like OpenCV)
    image = np.ones((300, 300, 3), dtype=np.uint8) * 255
    return image
