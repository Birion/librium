"""
Configuration management for the Librium application.

This module provides configuration classes for different environments:
- Development
- Testing
- Production

Usage:
    To use a specific configuration, set the FLASK_ENV environment variable to
    'development', 'testing', or 'production'.

    Alternatively, set the LIBRIUM_CONFIG environment variable to the fully qualified
    class name of the configuration to use, e.g., 'librium.core.config.DevelopmentConfig'.
"""

import os
from typing import Dict, Any, Type


class Config:
    """Base configuration class with common settings."""

    # Application name
    APPLICATION_NAME = os.getenv("APPLICATION_NAME", "Librium")

    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-please-change-in-production")
    DEBUG = False
    TESTING = False

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///librium.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/librium.log"

    # Asset settings
    ASSETS_DEBUG = False

    # Configure compression settings
    COMPRESS_LEVEL = 6  # Compression level (1-9, higher = more compression but slower)
    COMPRESS_MIN_SIZE = 500  # Only compress responses larger than this size (in bytes)

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-key-please-change-in-production")

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith("__") and not callable(value)
        }


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ASSETS_DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "DEBUG"

    # JWT defaults for tests to avoid missing-key errors
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-key-for-tests")
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_COOKIE_CSRF_PROTECT = False


class ProductionConfig(Config):
    """Production environment configuration."""

    # In production, SECRET_KEY should be set in environment variables
    SECRET_KEY = os.getenv("SECRET_KEY")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Ensure debug is off in production
    DEBUG = False
    ASSETS_DEBUG = False

    # Set stricter security headers
    STRICT_TRANSPORT_SECURITY = True
    CONTENT_SECURITY_POLICY = True


def get_config() -> Type[Config]:
    """
    Get the appropriate configuration class based on environment variables.

    Returns:
        The configuration class to use.
    """
    # Check for explicit configuration class
    config_class = os.getenv("LIBRIUM_CONFIG")
    if config_class:
        # Import the specified configuration class
        module_path, class_name = config_class.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)

    # Otherwise, use FLASK_ENV to determine configuration
    flask_env = os.getenv("FLASK_ENV", "development").lower()

    if flask_env == "production":
        return ProductionConfig
    elif flask_env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig
