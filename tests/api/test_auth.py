import pytest
from emova.api.core.security import get_password_hash

def test_login_success(api_client, mock_db_connection):
    """Test successful login with valid credentials."""
    # Setup mock DB return value for a user
    hashed_password = get_password_hash("password123")
    
    mock_db_connection["users"].find_one.return_value = {
        "email": "test@example.com",
        "passwordHash": hashed_password
    }
    
    response = api_client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_wrong_password(api_client, mock_db_connection):
    """Test login failure when password is incorrect."""
    hashed_password = get_password_hash("password123")
    
    mock_db_connection["users"].find_one.return_value = {
        "email": "test@example.com",
        "passwordHash": hashed_password
    }
    
    response = api_client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "El correo electrónico o la contraseña son incorrectos."

def test_login_failure_user_not_found(api_client, mock_db_connection):
    """Test login failure when the user does not exist in DB."""
    mock_db_connection["users"].find_one.return_value = None
    
    response = api_client.post(
        "/auth/login",
        data={"username": "notfound@example.com", "password": "password123"}
    )
    
    assert response.status_code == 401

def test_forgot_password(api_client, mock_db_connection):
    from unittest.mock import patch, AsyncMock
    mock_db_connection["users"].find_one.return_value = {"email": "test@example.com"}
    mock_db_connection["users"].update_one = AsyncMock()
    with patch("emova.api.routers.auth.send_recovery_email", new_callable=AsyncMock) as mock_send:
        response = api_client.post("/auth/forgot-password", json={"email": "test@example.com"})
        assert response.status_code == 200
        mock_send.assert_called_once()

def test_reset_password(api_client, mock_db_connection):
    from datetime import datetime, timezone, timedelta
    from unittest.mock import AsyncMock
    mock_db_connection["users"].find_one.return_value = {
        "email": "test@example.com",
        "recoveryCode": "123456",
        "recoveryCodeExpires": datetime.now(timezone.utc) + timedelta(minutes=10)
    }
    mock_db_connection["users"].update_one = AsyncMock()
    response = api_client.post("/auth/reset-password", json={"email": "test@example.com", "code": "123456", "new_password": "NewPassword1!"})
    assert response.status_code == 200
