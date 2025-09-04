"""
Settings management using Pydantic Settings.
Reads configuration from .env file and ensures required directories exist.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    
    # Storage and database settings
    storage_dir: str = Field(default="./data", alias="STORAGE_DIR")
    db_url: str = Field(default="sqlite:///./data/draws.db", alias="DB_URL")
    
    # HTTP client settings
    user_agent: str = Field(default="EuromillionsPro/1.0 (+contact)", alias="USER_AGENT")
    request_timeout: int = Field(default=15, alias="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    
    # API settings
    api_token: Optional[str] = Field(default=None, alias="API_TOKEN")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        base_path = Path(self.storage_dir)
        
        # Required directories
        directories = [
            base_path,
            base_path / "raw",
            base_path / "processed",
            Path("models") / "euromillions"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def storage_path(self) -> Path:
        """Get storage directory as Path object."""
        return Path(self.storage_dir)
    
    @property
    def raw_data_path(self) -> Path:
        """Get raw data directory as Path object."""
        return self.storage_path / "raw"
    
    @property
    def processed_data_path(self) -> Path:
        """Get processed data directory as Path object."""
        return self.storage_path / "processed"
    
    @property
    def models_path(self) -> Path:
        """Get models directory as Path object."""
        return Path("models") / "euromillions"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    Creates and initializes settings on first call.
    
    Returns:
        Settings: The application settings object
    """
    global _settings
    
    if _settings is None:
        _settings = Settings()
        _settings.ensure_directories()
    
    return _settings


def reload_settings() -> Settings:
    """
    Force reload of settings from environment/file.
    Useful for testing or when environment changes.
    
    Returns:
        Settings: The reloaded settings object
    """
    global _settings
    _settings = Settings()
    _settings.ensure_directories()
    return _settings


# Convenience function for quick access to common paths
def get_paths():
    """Get commonly used paths as a simple namespace object."""
    settings = get_settings()
    
    class Paths:
        storage = settings.storage_path
        raw = settings.raw_data_path
        processed = settings.processed_data_path
        models = settings.models_path
    
    return Paths()
