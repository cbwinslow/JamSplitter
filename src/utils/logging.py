"""
logging.py ─────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-24
Summary: Structured logging utility for JamSplitter
ModLog : 2025-05-24 Initial implementation
"""
import logging
import logging.config
import yaml
from pathlib import Path
from typing import Dict, Any

class Logger:
    """Custom logger with structured logging support"""

    @staticmethod
    def setup_logging(config_path: str = "config/logging.yaml") -> None:
        """
        Setup logging configuration from YAML file

        Args:
            config_path: Path to the logging configuration file
        """
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                raise FileNotFoundError(f"Logging configuration file not found: {config_path}")

            with open(config_path, 'r') as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)

        except Exception as e:
            logging.basicConfig(level=logging.INFO)
            logging.error(f"Failed to load logging configuration: {str(e)}")

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a structured logger instance

        Args:
            name: Logger name (usually __name__)

        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)

    @staticmethod
    def log_exception(e: Exception, context: Dict[str, Any] = None) -> None:
        """
        Log an exception with context

        Args:
            e: Exception to log
            context: Additional context information
        """
        if context is None:
            context = {}

        logger = logging.getLogger("jamsplitter")
        logger.error(
            "Exception occurred",
            extra={
                "exception": str(e),
                "type": type(e).__name__,
                **context
            }
        )

    @staticmethod
    def log_request(request: Dict[str, Any], response: Dict[str, Any] = None) -> None:
        """
        Log an API request and response

        Args:
            request: Request data
            response: Response data (optional)
        """
        logger = logging.getLogger("jamsplitter.api")

        log_data = {
            "method": request.get("method", "unknown"),
            "path": request.get("path", "unknown"),
            "query": request.get("query", {}),
            "status": response.get("status", "unknown") if response else "unknown",
            "duration_ms": response.get("duration_ms", 0) if response else 0
        }

        logger.info("API request", extra=log_data)
