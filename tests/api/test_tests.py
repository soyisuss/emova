import pytest
from bson import ObjectId
from unittest.mock import MagicMock

def test_create_test_template(api_client, mock_db_connection, mock_user):
    """Test creating a new test template."""
    mock_insert_result = type('obj', (object,), {'inserted_id': ObjectId()})()
    
    async def mock_find_one(query, *args, **kwargs):
        if "test_id" in query:
            return None  # Template does not exist yet
        return {"_id": mock_insert_result.inserted_id, "name": "Template 1", "test_id": "test-1", "user_id": str(mock_user.id), "tasks": [], "createdAt": "2026-01-01T00:00:00Z"}
        
    mock_db_connection["test_templates"].find_one = mock_find_one
    
    async def mock_insert(*args, **kwargs):
        return mock_insert_result
        
    mock_db_connection["test_templates"].insert_one = mock_insert

    response = api_client.post("/tests/templates/", json={"name": "Template 1", "test_id": "test-1", "tasks": []})
    
    assert response.status_code == 200
    assert response.json()["name"] == "Template 1"
    assert response.json()["test_id"] == "test-1"

def test_list_test_templates(api_client, mock_db_connection, mock_user):
    """Test listing all test templates for the user."""
    mock_cursor = MagicMock()
    
    # We mock the __aiter__ for the 'async for' loop in the endpoint
    async def async_generator():
        yield {"_id": ObjectId(), "name": "Template 1", "test_id": "t1", "user_id": str(mock_user.id), "tasks": [], "createdAt": "2026-01-01T00:00:00Z"}
        
    mock_cursor.__aiter__ = lambda self: async_generator()
    
    mock_db_connection["test_templates"].find = MagicMock()
    mock_db_connection["test_templates"].find.return_value.sort.return_value = mock_cursor
    
    response = api_client.get("/tests/templates/")
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Template 1"

def test_delete_test_template(api_client, mock_db_connection):
    """Test deleting a test template."""
    mock_delete_result = type('obj', (object,), {'deleted_count': 1})()
    
    async def mock_delete_one(*args, **kwargs):
        return mock_delete_result
        
    mock_db_connection["test_templates"].delete_one = mock_delete_one
    
    response = api_client.delete(f"/tests/templates/{str(ObjectId())}")
    
    assert response.status_code == 204
