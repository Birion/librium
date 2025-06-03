"""
Logging configuration for the Librium application.

This module provides a centralized place for configuring logging throughout the application.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Constants
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "librium.log"
DEFAULT_LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_LOG_BACKUP_COUNT = 5

# Create the logger
logger = logging.getLogger("librium")


def configure_logging(
    log_level=None,
    log_format=None,
    log_date_format=None,
    log_to_file=True,
    log_to_console=True,
    log_dir=None,
    log_file=None,
    log_max_bytes=None,
    log_backup_count=None,
):
    """
    Configure logging for the application.

    Args:
        log_level: The log level (default: INFO)
        log_format: The log format (default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_date_format: The log date format (default: "%Y-%m-%d %H:%M:%S")
        log_to_file: Whether to log to a file (default: True)
        log_to_console: Whether to log to the console (default: True)
        log_dir: The directory to store log files (default: "logs")
        log_file: The log file name (default: "librium.log")
        log_max_bytes: The maximum size of the log file before rotation (default: 10 MB)
        log_backup_count: The number of backup log files to keep (default: 5)
    """
    # Set default values if not provided
    log_level = log_level or DEFAULT_LOG_LEVEL
    log_format = log_format or DEFAULT_LOG_FORMAT
    log_date_format = log_date_format or DEFAULT_LOG_DATE_FORMAT
    log_dir = log_dir or DEFAULT_LOG_DIR
    log_file = log_file or DEFAULT_LOG_FILE
    log_max_bytes = log_max_bytes or DEFAULT_LOG_MAX_BYTES
    log_backup_count = log_backup_count or DEFAULT_LOG_BACKUP_COUNT

    # Configure the logger
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(log_format, log_date_format)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if requested
    if log_to_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Create file handler
        file_handler = RotatingFileHandler(
            log_path / log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Log that logging has been configured
    logger.info("Logging configured")


def get_logger(name):
    """
    Get a logger for the given name.

    Args:
        name: The name of the logger

    Returns:
        A logger instance
    """
    return logging.getLogger(f"librium.{name}")
