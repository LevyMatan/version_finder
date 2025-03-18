"""
Configuration for pytest. This file is automatically loaded by pytest.
"""
import os
import sys
import logging
import tempfile
import shutil
import pytest
from pathlib import Path

# Add the package to the path for test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


@pytest.fixture(scope="function")
def temp_log_dir():
    """Create a temporary directory for log files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after the test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def clean_logger_state():
    """Reset logger state before and after tests."""
    # Save original state
    original_manager = logging.Logger.manager
    original_root_handlers = logging.root.handlers.copy()
    original_environ = os.environ.copy()
    
    # Clear loggers
    logging.Logger.manager.loggerDict.clear()
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    yield
    
    # Restore original state
    os.environ.clear()
    os.environ.update(original_environ)
    logging.Logger.manager = original_manager
    logging.root.handlers = original_root_handlers 