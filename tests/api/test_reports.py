import pytest
from unittest.mock import patch
from bson import ObjectId

def test_list_reports(api_client, mock_db_connection, mock_user):
    """Test listing reports for the authenticated user."""
    from unittest.mock import MagicMock, AsyncMock
    # Setup mock
    mock_cursor = MagicMock()
    
    report_id = ObjectId()
    mock_cursor.to_list = AsyncMock(return_value=[
        {
            "_id": report_id,
            "reportUrl": "https://storage.googleapis.com/test/report.pdf",
            "userId": mock_user.id,
            "testName": "Test 1",
            "createdAt": "2026-01-01T00:00:00Z"
        }
    ])
    
    # Override find to be a normal mock that returns the cursor
    mock_db_connection["reports"].find = MagicMock(return_value=mock_cursor)
    
    response = api_client.get("/reports/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["testName"] == "Test 1"
    assert data[0]["userId"] == str(mock_user.id)

def test_create_report(api_client, mock_db_connection, mock_user):
    from unittest.mock import AsyncMock
    mock_insert_result = type('obj', (object,), {'inserted_id': ObjectId()})()
    mock_db_connection["reports"].insert_one = AsyncMock(return_value=mock_insert_result)
    mock_db_connection["reports"].find_one = AsyncMock(return_value={
        "_id": mock_insert_result.inserted_id, "userId": str(mock_user.id), "reportUrl": "http://", "testName": "T", "createdAt": "2026-01-01T00:00:00Z"
    })
    
    response = api_client.post("/reports/", json={"reportUrl": "http://", "userId": str(mock_user.id)})
    assert response.status_code == 201

@patch('emova.api.core.storage.StorageManager.upload_report_pdf')
def test_upload_report(mock_upload, api_client, mock_db_connection, mock_user):
    """Test uploading a PDF report."""
    mock_upload.return_value = "https://storage.googleapis.com/test/uploaded.pdf"
    
    # Mock insert
    mock_insert_result = type('obj', (object,), {'inserted_id': ObjectId()})
    
    async def mock_insert(*args, **kwargs):
        return mock_insert_result
    
    mock_db_connection["reports"].insert_one = mock_insert
    
    # Mock find_one after insert
    async def mock_find_one(*args, **kwargs):
        return {
            "_id": mock_insert_result.inserted_id,
            "reportUrl": "https://storage.googleapis.com/test/uploaded.pdf",
            "userId": mock_user.id,
            "testName": "Prueba Upload",
            "createdAt": "2026-01-01T00:00:00Z"
        }
    
    mock_db_connection["reports"].find_one = mock_find_one
    
    # Create dummy PDF file
    files = {"file": ("test.pdf", b"%PDF-1.4...", "application/pdf")}
    data = {"testName": "Prueba Upload"}
    
    response = api_client.post("/reports/upload", files=files, data=data)
    
    assert response.status_code == 201
    assert response.json()["reportUrl"] == "https://storage.googleapis.com/test/uploaded.pdf"
    assert response.json()["testName"] == "Prueba Upload"
    mock_upload.assert_called_once()

def test_read_report(api_client, mock_db_connection, mock_user):
    from unittest.mock import AsyncMock
    mock_db_connection["reports"].find_one = AsyncMock(return_value={
        "_id": ObjectId(), "userId": str(mock_user.id), "reportUrl": "http://", "testName": "T", "createdAt": "2026-01-01T00:00:00Z"
    })
    response = api_client.get(f"/reports/{str(ObjectId())}")
    assert response.status_code == 200

def test_download_report(api_client, mock_db_connection, mock_user):
    from unittest.mock import AsyncMock, patch
    mock_db_connection["reports"].find_one = AsyncMock(return_value={
        "_id": ObjectId(), "userId": str(mock_user.id), "reportUrl": "http://", "testName": "T", "createdAt": "2026-01-01T00:00:00Z"
    })
    with patch("emova.api.core.storage.StorageManager.download_report_pdf", new_callable=AsyncMock) as mock_dl:
        mock_dl.return_value = b"%PDF-1.4"
        response = api_client.get(f"/reports/{str(ObjectId())}/download")
        assert response.status_code == 200
        assert response.content == b"%PDF-1.4"

def test_delete_report(api_client, mock_db_connection, mock_user):
    from unittest.mock import AsyncMock
    mock_db_connection["reports"].find_one = AsyncMock(return_value={
        "_id": ObjectId(), "userId": str(mock_user.id)
    })
    mock_db_connection["reports"].delete_one = AsyncMock()
    response = api_client.delete(f"/reports/{str(ObjectId())}")
    assert response.status_code == 204
