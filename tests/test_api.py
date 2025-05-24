"""
test_api.py ─────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-24
Summary: Test suite for JamSplitter API endpoints
ModLog : 2025-05-24 Initial implementation
"""
import pytest
from fastapi.testclient import TestClient
from app import app
from utils.logging import Logger
from utils.monitoring import Metrics
from utils.test_utils import TestHelper
import time

@pytest.fixture(scope="module")
def test_client():
    """Create test client for API endpoints"""
    client = TestClient(app)
    return client

@pytest.fixture(scope="module")
def test_data():
    """Load test data"""
    return TestHelper.load_test_data("test_data.json")

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
