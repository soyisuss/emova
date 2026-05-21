import pytest
from bson import ObjectId
from unittest.mock import AsyncMock

def test_create_user(api_client, mock_db_connection):
    """Test user registration."""
    # Check if user exists -> return None
    mock_insert_result = type('obj', (object,), {'inserted_id': ObjectId()})()
    
    async def mock_find_one(query, *args, **kwargs):
        if "email" in query:
            return None  # User does not exist
        # Return newly created user when queried by ID
        return {"_id": mock_insert_result.inserted_id, "email": "new@example.com"}
        
    mock_db_connection["users"].find_one = mock_find_one
    
    async def mock_insert(*args, **kwargs):
        return mock_insert_result
        
    mock_db_connection["users"].insert_one = mock_insert

    response = api_client.post("/users/", json={"email": "new@example.com", "password": "Password1!"})
    
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"

def test_create_user_already_exists(api_client, mock_db_connection):
    async def mock_find_one(query, *args, **kwargs):
        return {"email": "exists@example.com"}
    mock_db_connection["users"].find_one = mock_find_one

    response = api_client.post("/users/", json={"email": "exists@example.com", "password": "Password1!"})
    assert response.status_code == 400

def test_read_current_user(api_client, mock_user):
    """Test retrieving current user profile."""
    response = api_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == mock_user.email

def test_update_current_user(api_client, mock_db_connection, mock_user):
    """Test updating user profile."""
    # Assume the new email doesn't belong to another user
    mock_db_connection["users"].find_one = AsyncMock(side_effect=[
        None,  # No other user has this email
        {"_id": mock_user.id, "email": "updated@example.com"} # Updated user doc
    ])
    
    mock_db_connection["users"].update_one = AsyncMock()
    
    response = api_client.patch("/users/me", json={"email": "updated@example.com"})
    
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"

def test_delete_current_user(api_client, mock_db_connection):
    """Test deleting the current user."""
    mock_db_connection["users"].delete_one = AsyncMock()
    
    response = api_client.delete("/users/me")
    
    assert response.status_code == 204

def test_update_password(api_client, mock_db_connection, mock_user):
    from emova.api.core.security import get_password_hash
    mock_user.passwordHash = get_password_hash("OldPassword1!")
    mock_db_connection["users"].update_one = AsyncMock()
    
    response = api_client.put("/users/me/password", json={"old_password": "OldPassword1!", "new_password": "NewPassword1!"})
    assert response.status_code == 200
