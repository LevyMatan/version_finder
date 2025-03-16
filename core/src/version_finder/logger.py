"""
logger.py
====================================
Logging configuration for version_finder.
This module provides a centralized logging configuration.
"""
from platformdirs import user_log_dir
import os
import logging
import sys
from typing import Dict, Optional


class ColoredFormatter(logging.Formatter):
    """Formatter that adds color to console log messages based on their level."""
    COLOR_CODES = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[32m",     # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",    # Red
        logging.CRITICAL: "\033[41m",  # Red background
    }
    RESET_CODE = "\033[0m"

    def format(self, record):
        color = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        message = super().format(record)
        return f"{color}{message}{self.RESET_CODE}"


# Global logger cache to ensure we don't create multiple loggers
_loggers: Dict[str, logging.Logger] = {}


def _ensure_log_directory(custom_dir=None):
    """
    Ensure the log directory exists and is writable.

    Args:
        custom_dir: Optional custom directory path

    Returns:
        tuple: (log_dir, success)
    """
    if custom_dir:
        log_dir = custom_dir
    else:
        log_dir = user_log_dir("version_finder", appauthor=False)

    try:
        # Create the directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Test if we can write to the directory
        test_file = os.path.join(log_dir, "test_write.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return log_dir, True
        except (IOError, PermissionError):
            print(f"Warning: Cannot write to log directory: {log_dir}")
            return log_dir, False
    except Exception as e:
        print(f"Warning: Failed to create log directory {log_dir}: {e}")
        return log_dir, False


def get_logger(name: str = "version_finder", verbose: bool = False) -> logging.Logger:
    """
    Get a logger with the specified name. If the logger already exists, return it.

    Args:
        name: The name of the logger
        verbose: Whether to enable verbose logging

    Returns:
        logging.Logger: The configured logger
    """
    # Check if we already have this logger configured
    if name in _loggers:
        return _loggers[name]

    # Create a new logger
    logger = logging.getLogger(name)

    # Only configure the logger if it hasn't been configured yet
    if not logger.handlers:
        # Set the base level to DEBUG so handlers can filter from there
        logger.setLevel(logging.DEBUG)

        # Configure console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_level = logging.DEBUG if verbose else logging.INFO
        console_handler.setLevel(console_level)
        console_formatter = ColoredFormatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Configure file handler
        log_dir, dir_writable = _ensure_log_directory()

        if dir_writable:
            # Primary log file in the standard location
            log_file_path = os.path.join(log_dir, f"{name}.log")
            try:
                file_handler = logging.FileHandler(log_file_path)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
                logger.info(f"Log file created at: {log_file_path}")
            except Exception as e:
                print(f"Warning: Failed to create log file at {log_file_path}: {e}")
                dir_writable = False

        if not dir_writable:
            # Fallback to current directory
            fallback_path = os.path.join(os.getcwd(), f"{name}.log")
            try:
                file_handler = logging.FileHandler(fallback_path)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
                logger.info(f"Using fallback log file at: {fallback_path}")
            except Exception as e:
                print(f"Warning: Failed to create fallback log file: {e}")
                # Continue without file logging

    # Cache the logger
    _loggers[name] = logger

    return logger


def configure_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """
    Configure global logging settings.

    Args:
        verbose: Whether to enable verbose logging
        log_file: Optional custom log file path
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set the root logger level
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_level = logging.DEBUG if verbose else logging.INFO
    console_handler.setLevel(console_level)
    console_formatter = ColoredFormatter('%(name)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Configure file handler if specified
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            log_dir, dir_writable = _ensure_log_directory(log_dir)

            if dir_writable:
                try:
                    file_handler = logging.FileHandler(log_file)
                    file_handler.setLevel(logging.DEBUG)
                    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                    file_handler.setFormatter(file_formatter)
                    root_logger.addHandler(file_handler)
                except Exception as e:
                    print(f"Warning: Failed to set up file logging to {log_file}: {e}")
            else:
                print(f"Warning: Log directory {log_dir} is not writable")
