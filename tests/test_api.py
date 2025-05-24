"""
test_api.py ─────────────────────────────────────────────────────────────
Test suite for JamSplitter API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

# Test data
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
TEST_FORMAT = "mp3"

@pytest.fixture(scope="module")
def test_client():
    """Create test client for API endpoints"""
    return TestClient(app)

def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
    assert "services" in response.json()
    assert "database" in response.json()["services"]

def test_process_audio_job(test_client):
    """Test submitting a new audio processing job"""
    response = test_client.post(
        "/api/process",
        json={"url": TEST_VIDEO_URL, "format": TEST_FORMAT}
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert "job_id" in data
    assert "status" in data
    assert data["status"] in ["queued", "processing"]
    return data["job_id"]

def test_get_job_status(test_client):
    """Test getting job status"""
    # First submit a job
    job_id = test_process_audio_job(test_client)
    
    # Then check its status
    response = test_client.get(f"/api/jobs/{job_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "progress" in data
    assert isinstance(data["progress"], int)
    assert 0 <= data["progress"] <= 100

def test_get_nonexistent_job_status(test_client):
    """Test getting status for a non-existent job"""
    response = test_client.get("/api/jobs/nonexistent-job-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_invalid_url_processing(test_client):
    """Test submitting an invalid URL for processing"""
    response = test_client.post(
        "/api/process",
        json={"url": "not-a-valid-url", "format": TEST_FORMAT}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_missing_required_fields(test_client):
    """Test submitting a request with missing required fields"""
    # Missing URL
    response = test_client.post(
        "/api/process",
        json={"format": TEST_FORMAT}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Missing format
    response = test_client.post(
        "/api/process",
        json={"url": TEST_VIDEO_URL}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_http_method(test_client):
    """Test using an invalid HTTP method"""
    response = test_client.put("/health")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

def test_api_documentation_page(test_client):
    """Test the API documentation page is accessible"""
    response = test_client.get("/docs/api")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    assert "API Documentation" in response.text

def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/api/health")
    TestHelper.assert_response(response, 200, {"status": "healthy"})

def test_split_video_success(test_client, test_data):
    """Test successful video split"""
    video_data = test_data["valid_video"]
    response = test_client.post(
        "/api/split",
        json={"url": video_data["url"], "format": video_data["format"]}
    )
    TestHelper.assert_response(response, 200, test_data["response_success"])

def test_split_video_failure(test_client, test_data):
    """Test video split with invalid URL"""
    video_data = test_data["invalid_video"]
    response = test_client.post(
        "/api/split",
        json={"url": video_data["url"], "format": video_data["format"]}
    )
    TestHelper.assert_response(response, 400, test_data["response_error"])

def test_get_status(test_client, test_data):
    """Test status endpoint"""
    video_data = test_data["valid_video"]
    response = test_client.get(f"/api/status/{video_data['url']}")
    assert response.status_code == 200
    assert "status" in response.json()

def test_get_queue(test_client):
    """Test queue endpoint"""
    response = test_client.get("/api/queue")
    TestHelper.assert_response(response, 200)
    assert isinstance(response.json(), dict)

def test_api_docs(test_client):
    """Test API documentation endpoints"""
    response = test_client.get("/api/docs")
    assert response.status_code == 307  # Redirect
    
    response = test_client.get("/api/redoc")
    assert response.status_code == 307  # Redirect

def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    metrics = Metrics()
    assert metrics.port == 8001
    
    # Test request tracking
    metrics.track_request("GET", "/test", "200", 0.1)
    
    # Test processing tracking
    metrics.track_processing("success", 1.0)
    
    # Test queue size
    metrics.update_queue_size(5)
