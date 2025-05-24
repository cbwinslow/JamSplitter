"""
monitoring.py ─────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-24
Summary: Prometheus metrics utility for JamSplitter
ModLog : 2025-05-24 Initial implementation
"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Dict, Any
import time

class Metrics:
    """Prometheus metrics collector for JamSplitter"""

    def __init__(self, port: int = 8001):
        """
        Initialize metrics collector

        Args:
            port: Port for Prometheus metrics server
        """
        self.port = port

        # Request metrics
        self.requests_total = Counter(
            'jamsplitter_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )

        self.request_duration = Histogram(
            'jamsplitter_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )

        # Processing metrics
        self.processing_total = Counter(
            'jamsplitter_processing_total',
            'Total number of processing tasks',
            ['status']
        )

        self.processing_duration = Histogram(
            'jamsplitter_processing_duration_seconds',
            'Processing duration in seconds'
        )

        # Queue metrics
        self.queue_size = Gauge(
            'jamsplitter_queue_size',
            'Number of items in processing queue'
        )

        # Start metrics server
        start_http_server(self.port)

    def track_request(self, method: str, endpoint: str, status: str, duration: float) -> None:
        """
        Track a request

        Args:
            method: HTTP method
            endpoint: Request endpoint
            status: Response status
            duration: Request duration in seconds
        """
        self.requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def track_processing(self, status: str, duration: float) -> None:
        """
        Track processing task

        Args:
            status: Processing status
            duration: Processing duration in seconds
        """
        self.processing_total.labels(status=status).inc()
        self.processing_duration.observe(duration)

    def update_queue_size(self, size: int) -> None:
        """
        Update queue size metric

        Args:
            size: Current queue size
        """
        self.queue_size.set(size)

    def track_error(self, error_type: str, context: Dict[str, Any]) -> None:
        """
        Track an error

        Args:
            error_type: Type of error
            context: Error context
        """
        self.processing_total.labels(status="error").inc()

    def track_success(self, context: Dict[str, Any]) -> None:
        """
        Track a successful operation

        Args:
            context: Operation context
        """
        self.processing_total.labels(status="success").inc()
