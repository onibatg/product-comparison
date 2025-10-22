"""
Application configuration settings.

This module defines application configuration using Pydantic's settings
management. Settings can be configured via environment variables or a
.env file, following the twelve-factor app methodology.
"""

import logging
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via environment variables with the
    prefix 'APP_'. For example, APP_LOG_LEVEL will override log_level.

    Attributes:
        app_name: Application name
        app_version: Application version
        api_version: API version prefix (e.g., 'v1')
        environment: Deployment environment (development, staging, production)
        log_level: Logging level
        data_file_path: Path to the product data JSON file
        host: API server host
        port: API server port
        reload: Enable auto-reload on code changes (development only)
        cors_origins: Allowed CORS origins
    """

    # Application metadata
    app_name: str = "Item Comparison API"
    app_version: str = "1.0.0"
    api_version: str = "v1"
    environment: Literal["development", "staging", "production"] = "development"

    # Logging configuration
    log_level: str = "INFO"

    # Data configuration
    data_file_path: str = "data/products.json"

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # CORS configuration
    cors_origins: list[str] = ["*"]

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def api_prefix(self) -> str:
        """
        Get the API URL prefix.

        Returns:
            API prefix path (e.g., '/api/v1')
        """
        return f"/api/{self.api_version}"

    @property
    def data_file_absolute_path(self) -> Path:
        """
        Get the absolute path to the data file.

        Returns:
            Absolute Path object for the data file
        """
        return Path(self.data_file_path).resolve()

    def configure_logging(self) -> None:
        """
        Configure application logging based on settings.

        Sets up logging format, level, and handlers according to the
        configured log level and environment.
        """
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
            ]
        )

        # Set third-party loggers to WARNING to reduce noise
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    def get_summary(self) -> dict:
        """
        Get a summary of current settings for logging/debugging.

        Returns:
            Dictionary of key settings (excludes sensitive information)
        """
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "api_version": self.api_version,
            "environment": self.environment,
            "log_level": self.log_level,
            "data_file_path": self.data_file_path,
            "host": self.host,
            "port": self.port,
            "api_prefix": self.api_prefix,
        }


# Global settings instance
# This can be imported and used throughout the application
settings = Settings()
