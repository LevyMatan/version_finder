# version_finder/logger.py
from platformdirs import user_log_dir
import os
import logging
import sys


class ColoredFormatter(logging.Formatter):
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


def setup_logger(verbose: bool = False) -> logging.Logger:
    # Create a logger
    logger = logging.getLogger("version_finder")
    if logger.hasHandlers():
        logger.debug("Logger already initialized. Skipping setup.")
        return logger  # Avoid duplicate handlers
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_log_level = logging.DEBUG if verbose else logging.INFO
    console_handler.setLevel(console_log_level)
    # Formatter
    console_formatter = ColoredFormatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Determine log file path
    log_dir = user_log_dir("version_finder", appauthor=False)
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "app.log")

    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    # Formatter
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"Log file created at: {log_file_path}")

    return logger
