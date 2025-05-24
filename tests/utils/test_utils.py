"""
test_utils.py ─────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-24
Summary: Test utility functions for JamSplitter
ModLog : 2025-05-24 Initial implementation
"""
import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any
import json

class TestHelper:
    """Test helper class with utility methods"""
    
    @staticmethod
    def load_test_data(filename: str) -> Dict[str, Any]:
        """
        Load test data from JSON file
        
        Args:
            filename: Name of the test data file
            
        Returns:
            Dictionary containing test data
        """
        test_data_dir = Path(__file__).parent / "data"
        with open(test_data_dir / filename, 'r') as f:
            return json.load(f)
    
    @staticmethod
    async def wait_for_condition(condition: callable, timeout: float = 5.0, interval: float = 0.1) -> None:
        """
        Wait for a condition to be true
        
        Args:
            condition: Callable that returns boolean
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds
            
        Raises:
            TimeoutError: If condition is not met within timeout
        """
        start_time = time.time()
        while not condition():
            if time.time() - start_time > timeout:
                raise TimeoutError("Condition not met within timeout")
            await asyncio.sleep(interval)
    
    @staticmethod
    def assert_response(response: Any, expected_status: int, expected_data: Dict[str, Any] = None) -> None:
        """
        Assert response matches expected values
        
        Args:
            response: Response object
            expected_status: Expected status code
            expected_data: Expected response data
        """
        assert response.status_code == expected_status
        if expected_data is not None:
            assert response.json() == expected_data
    
    @staticmethod
    def create_test_video() -> Dict[str, Any]:
        """
        Create test video data
        
        Returns:
            Dictionary containing test video data
        """
        return {
            "url": "https://test.youtube.com/video",
            "title": "Test Video",
            "duration": 180,
            "format": "mp3"
        }
