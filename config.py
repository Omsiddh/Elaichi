"""
Configuration management for Travel Planner
Handles API keys, settings, and environment variables
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    openweather_api_key: str = Field(default="", alias="OPENWEATHER_API_KEY")
    serpapi_key: Optional[str] = Field(default=None, alias="SERPAPI_KEY")
    
    # Application settings
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    
    # LLM settings  
    gemini_model: str = "models/gemini-2.5-pro"  # Full model path for new API
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # API endpoints
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_required_keys(self) -> bool:
        """Validate that required API keys are present"""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required. Get it from https://makersuite.google.com/app/apikey")
        if not self.openweather_api_key:
            raise ValueError("OPENWEATHER_API_KEY is required. Get it from https://openweathermap.org/api")
        return True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global _settings
    _settings = Settings()
    return _settings


# Export for easy import
__all__ = ["Settings", "get_settings", "reload_settings"]
