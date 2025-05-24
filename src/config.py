"""Configuration management for JamSplitter."""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Centralized configuration management."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Optional path to config file
        """
        self.config_path = config_path or os.getenv('JAMSPLITTER_CONFIG', 'config.yaml')
        self.config = self._load_config()
        self._update_from_env()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
    
    def _update_from_env(self):
        """Update configuration from environment variables."""
        for key, value in os.environ.items():
            if key.startswith('JAMSPLITTER_'):
                config_key = key[12:].lower()  # Remove JAMSPLITTER_ prefix
                self.config[config_key] = self._parse_env_value(value)
    
    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dict-like access."""
        return self.config[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in config."""
        return key in self.config

# Global config instance
config = Config()

def get_config() -> Config:
    """Get the global config instance."""
    return config
