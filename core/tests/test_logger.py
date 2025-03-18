"""
Tests for the logger module.
"""
import os
import sys
import tempfile
import logging
from pathlib import Path
import unittest
from unittest import mock
import shutil

from version_finder.logger import (
    get_default_log_dir,
    _ensure_log_directory,
    get_logger,
    get_current_log_file_path,
    LOG_DIR_ENV_VAR
)


class TestLogger(unittest.TestCase):
    """Test cases for the logger module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_dir = Path(self.temp_dir) / "test_logs"
        
        # Save original environ to restore later
        self.original_environ = os.environ.copy()
        
        # Clear any existing loggers to avoid test interference
        logging.Logger.manager.loggerDict.clear()
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_environ)
        
        # Clear loggers again after tests
        logging.Logger.manager.loggerDict.clear()

    def test_get_default_log_dir_env_var(self):
        """Test that get_default_log_dir respects environment variable."""
        os.environ[LOG_DIR_ENV_VAR] = self.temp_dir
        log_dir = get_default_log_dir()
        self.assertEqual(log_dir, Path(self.temp_dir))

    def test_get_default_log_dir_windows(self):
        """Test get_default_log_dir on Windows."""
        with mock.patch('sys.platform', 'win32'):
            with mock.patch.dict(os.environ, {'LOCALAPPDATA': self.temp_dir}, clear=True):
                log_dir = get_default_log_dir()
                expected = Path(self.temp_dir) / "version_finder" / "Logs"
                self.assertEqual(log_dir, expected)

    def test_get_default_log_dir_macos(self):
        """Test get_default_log_dir on macOS."""
        with mock.patch('sys.platform', 'darwin'):
            with mock.patch('pathlib.Path.home', return_value=Path(self.temp_dir)):
                log_dir = get_default_log_dir()
                expected = Path(self.temp_dir) / "Library" / "Logs" / "version_finder"
                self.assertEqual(log_dir, expected)

    def test_get_default_log_dir_linux(self):
        """Test get_default_log_dir on Linux."""
        with mock.patch('sys.platform', 'linux'):
            with mock.patch('pathlib.Path.home', return_value=Path(self.temp_dir)):
                log_dir = get_default_log_dir()
                expected = Path(self.temp_dir) / ".local" / "share" / "version_finder" / "logs"
                self.assertEqual(log_dir, expected)

    def test_get_default_log_dir_linux_xdg(self):
        """Test get_default_log_dir on Linux with XDG_DATA_HOME set."""
        with mock.patch('sys.platform', 'linux'):
            xdg_dir = os.path.join(self.temp_dir, "xdg_data")
            with mock.patch.dict(os.environ, {'XDG_DATA_HOME': xdg_dir}, clear=True):
                log_dir = get_default_log_dir()
                expected = Path(xdg_dir) / "version_finder" / "logs"
                self.assertEqual(log_dir, expected)

    def test_ensure_log_directory_custom(self):
        """Test _ensure_log_directory with custom dir."""
        # Create the test directory
        self.test_log_dir.mkdir(parents=True, exist_ok=True)
        
        log_dir, success = _ensure_log_directory(self.test_log_dir)
        self.assertTrue(success)
        self.assertEqual(log_dir, str(self.test_log_dir))
        
        # Verify test file was created and removed
        test_files = list(self.test_log_dir.glob("*.tmp"))
        self.assertEqual(len(test_files), 0)

    def test_get_logger(self):
        """Test get_logger creates a proper logger."""
        # Set up environment for predictable log location
        os.environ[LOG_DIR_ENV_VAR] = self.temp_dir
        
        logger = get_logger("test_logger")
        
        # Verify logger properties
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.DEBUG)
        
        # Check handlers
        self.assertGreaterEqual(len(logger.handlers), 1)  # At least console handler
        
        # Check if there's a file handler
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        if file_handlers:  # May not have file handler if directory not writable
            # Test logging
            test_message = "Test log message"
            logger.info(test_message)
            
            # Check log file content
            handler = file_handlers[0]
            with open(handler.baseFilename, 'r') as f:
                log_content = f.read()
                self.assertIn("Log initialized", log_content)
                self.assertIn(test_message, log_content)

    def test_get_current_log_file_path(self):
        """Test get_current_log_file_path returns the correct path."""
        # Create a logger with a file handler
        os.environ[LOG_DIR_ENV_VAR] = self.temp_dir
        self.test_log_dir.mkdir(parents=True, exist_ok=True)
        
        test_log_file = self.test_log_dir / "test_logger.log"
        test_log_file.write_text("Initial log content\n")
        
        logger = logging.getLogger("test_logger_path")
        handler = logging.FileHandler(str(test_log_file))
        logger.addHandler(handler)
        
        # Test get_current_log_file_path
        log_path = get_current_log_file_path("test_logger_path")
        self.assertEqual(log_path, str(test_log_file))

    def test_get_current_log_file_path_no_handler(self):
        """Test get_current_log_file_path with no file handler."""
        # Create logger with only stream handler
        logger = logging.getLogger("test_logger_no_file")
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        
        # Configure test environment
        log_dir = Path(self.temp_dir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        today_log = log_dir / f"test_logger_no_file-{os.path.basename(log_dir)}.log"
        today_log.write_text("Test log content\n")
        
        with mock.patch('version_finder.logger._ensure_log_directory', 
                        return_value=(str(log_dir), True)):
            # Should find log file in the log directory
            with mock.patch('version_finder.logger.get_default_log_dir',
                           return_value=log_dir):
                log_path = get_current_log_file_path("test_logger_no_file")
                self.assertIsNotNone(log_path)


if __name__ == '__main__':
    unittest.main() 