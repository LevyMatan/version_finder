"""
logger.py
====================================
Logging configuration for version_finder.
This module provides a centralized logging configuration.
"""
from datetime import datetime
import os
import logging
import sys
import tempfile
from typing import Optional, Tuple
from pathlib import Path


# Environment variable to override default log directory
LOG_DIR_ENV_VAR = "VERSION_FINDER_LOG_DIR"


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


def get_default_log_dir() -> Path:
    """
    Get the default log directory based on the operating system.
    Respects VERSION_FINDER_LOG_DIR environment variable if set.
    
    Returns:
        Path object for the default log directory
    """
    # First check environment variable 
    env_log_dir = os.environ.get(LOG_DIR_ENV_VAR)
    if env_log_dir:
        return Path(env_log_dir)
    
    app_name = "version_finder"
    
    try:
        if sys.platform.startswith('win'):
            # Windows: %LOCALAPPDATA%\version_finder\Logs
            base_dir = os.environ.get('LOCALAPPDATA')
            if not base_dir or not os.path.exists(base_dir):
                base_dir = os.path.expanduser('~\\AppData\\Local')
            return Path(base_dir) / app_name / "Logs"
        elif sys.platform.startswith('darwin'):
            # macOS: ~/Library/Logs/version_finder
            return Path.home() / "Library" / "Logs" / app_name
        else:
            # Linux/Unix: ~/.local/share/version_finder/logs
            xdg_data_home = os.environ.get('XDG_DATA_HOME')
            if xdg_data_home:
                return Path(xdg_data_home) / app_name / "logs"
            return Path.home() / ".local" / "share" / app_name / "logs"
    except Exception:
        # Fallback to temp directory if something goes wrong
        return Path(tempfile.gettempdir()) / app_name / "logs"

def _ensure_log_directory(custom_dir: Optional[Path] = None) -> Tuple[str, bool]:
    """
    Ensure the log directory exists and is writable.
    Falls back to temporary directory if the primary location fails.

    Args:
        custom_dir: Optional custom directory path

    Returns:
        tuple: (log_dir_path, success)
    """
    # Try the primary path first
    primary_paths = []
    
    # Add custom directory if provided
    if custom_dir:
        primary_paths.append(Path(custom_dir))
    
    # Then try the default path
    primary_paths.append(get_default_log_dir())
    
    # Try each location
    for log_dir_path in primary_paths:
        try:
            # Create the directory if it doesn't exist
            log_dir_path.mkdir(parents=True, exist_ok=True)

            # Test if we can write to the directory
            test_file = log_dir_path / "test_write.tmp"
            
            try:
                test_file.write_text("test")
                test_file.unlink()  # Remove the file
                return str(log_dir_path), True
            except Exception:
                # Can't write to this directory, try the next one
                continue
        except Exception:
            # Can't create this directory, try the next one
            continue
    
    # If all primary paths fail, try using the system temp directory
    try:
        temp_dir = Path(tempfile.gettempdir()) / "version_finder" / "logs"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Test if we can write to the temp directory
        test_file = temp_dir / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()  # Remove the file
            return str(temp_dir), True
        except Exception:
            # Even temp directory isn't writable, give up
            pass
    except Exception:
        # Can't create temp directory either
        pass
    
    # None of the paths worked
    return str(primary_paths[0] if primary_paths else "unknown"), False

def get_logger(name: str = "version_finder") -> logging.Logger:
    """
    Get a logger with the specified name. If the logger already exists, return it.

    Args:
        name: The name of the logger
        verbose: Whether to enable verbose logging

    Returns:
        logging.Logger: The configured logger
    """

    # Create a new logger
    logger = logging.getLogger(name)

    # Only configure the logger if it hasn't been configured yet
    if not logger.handlers:
        # Set the base level to DEBUG so handlers can filter from there
        logger.setLevel(logging.DEBUG)

        # Configure console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # Configure file handler
        log_dir, dir_writable = _ensure_log_directory()

        if dir_writable:
            # Primary log file in the standard location
            log_file_name = f"{name}-{datetime.now().strftime('%Y-%m-%d')}.log"
            log_file_path = Path(log_dir) / log_file_name

            try:
                # Try to write directly to file first as a test
                log_file_path.write_text(f"Log initialized: {datetime.now().isoformat()}\n")
                
                if log_file_path.exists():
                    file_size = log_file_path.stat().st_size
                else:
                    # Try to diagnose the issue
                    if sys.platform.startswith('win'):
                        print(f"Windows path length: {len(str(log_file_path))} characters")
                        if len(str(log_file_path)) > 260:
                            print("Path exceeds Windows 260 character limit")
                
                # Now set up the logging handler
                file_handler = logging.FileHandler(str(log_file_path))
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(message)s')
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
                logger.debug(f"Log file created at: {str(log_file_path)}")
                file_handler.flush()
                
            except Exception as e:
                import traceback
                print(f"Warning: Failed to create log file at {str(log_file_path)}: {str(e)}")
                print(f"Exception type: {type(e).__name__}")
                print(f"Exception details: {traceback.format_exc()}")
                dir_writable = False
                log_file_path = None

        if not dir_writable:
            # Fallback to current directory
            fallback_dir = Path.cwd()
            fallback_path = fallback_dir / f"{name}.log"
            
            # List directory contents before creating fallback log
            if fallback_dir.exists():
                for file_path in fallback_dir.iterdir():
                    if file_path.name.endswith('.log'):  # Only show log files to avoid cluttering output
                        file_size = file_path.stat().st_size
                        print(f"  - {file_path.name} ({file_size} bytes)")
            else:
                print("  Directory does not exist!")
                
            try:
                # Try to write directly to file first as a test
                fallback_path.write_text(f"Fallback log initialized: {datetime.now().isoformat()}\n")
                
                if fallback_path.exists():
                    print(f"Verified fallback log file exists at: {str(fallback_path)}")
                    file_size = fallback_path.stat().st_size
                    print(f"Fallback log file size: {file_size} bytes")
                else:
                    print(f"ERROR: Fallback file was written but doesn't exist at: {str(fallback_path)}")
                
                # Now set up the logging handler
                file_handler = logging.FileHandler(str(fallback_path))
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
                logger.debug(f"Using fallback log file at: {str(fallback_path)}")
                log_file_path = str(fallback_path)
                file_handler.flush()
                
            except Exception as e:
                import traceback
                print(f"Warning: Failed to create fallback log file: {str(e)}")
                print(f"Exception type: {type(e).__name__}")
                print(f"Exception details: {traceback.format_exc()}")
                log_file_path = None
                # Continue without file logging

        # Test the log file was created
        if log_file_path and Path(log_file_path).exists():
            logger.info(f"Logging to file: {str(log_file_path)}")
        else:
            logger.warning("File logging not available")

    return logger


def configure_logging(verbose: bool = False, log_file_path: Optional[Path] = None) -> None:
    """
    Configure global logging settings.

    Args:
        verbose: Whether to enable verbose logging
        log_file_path: Optional custom log file path
    """
    logger = get_logger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if log_file_path and isinstance(log_file_path, Path):
        log_dir = str(log_file_path.parent) if log_file_path.parent != Path() else None
        if log_dir:
            log_dir, dir_writable = _ensure_log_directory(log_dir)
            if dir_writable:
                try:
                    # List directory contents before creating custom log
                    log_dir_path = Path(log_dir)
                    print(f"Contents of {str(log_dir_path)} before creating custom log:")
                    if log_dir_path.exists():
                        for file_path in log_dir_path.iterdir():
                            file_size = file_path.stat().st_size
                            print(f"  - {file_path.name} ({file_size} bytes)")
                    else:
                        print("  Directory does not exist!")
                    
                    # Try to write directly to file first as a test
                    log_file_path.write_text(f"Custom log initialized: {datetime.now().isoformat()}\n")
                    
                    if log_file_path.exists():
                        print(f"Verified custom log file exists at: {str(log_file_path)}")
                        file_size = log_file_path.stat().st_size
                        print(f"Custom log file size: {file_size} bytes")
                    else:
                        print(f"ERROR: Custom file was written but doesn't exist at: {str(log_file_path)}")
                    
                    # Now set up the logging handler
                    file_handler = logging.FileHandler(str(log_file_path))
                    file_handler.setLevel(logging.DEBUG)
                    file_formatter = logging.Formatter('%(asctime)s - %(message)s')
                    file_handler.setFormatter(file_formatter)
                    logger.addHandler(file_handler)
                    logger.info(f"Log file created at: {str(log_file_path)}")
                    file_handler.flush()
                    
                    # List directory contents after creating custom log
                    print(f"Contents of {str(log_dir_path)} after creating custom log:")
                    if log_dir_path.exists():
                        for file_path in log_dir_path.iterdir():
                            file_size = file_path.stat().st_size
                            print(f"  - {file_path.name} ({file_size} bytes)")
                    else:
                        print("  Directory does not exist!")
                except Exception as e:
                    import traceback
                    print(f"Warning: Failed to create log file at {str(log_file_path)}: {str(e)}")
                    print(f"Exception type: {type(e).__name__}")
                    print(f"Exception details: {traceback.format_exc()}")
            else:
                print(f"Warning: Log directory {str(log_dir)} is not writable")

def get_current_log_file_path(name: str = "version_finder") -> Optional[str]:
    """
    Get the path to the current log file for the given logger name.
    
    Args:
        name: Logger name
        
    Returns:
        Path to the current log file or None if no file handler is found
    """
    try:
        logger = logging.getLogger(name)
        
        # Search for file handlers in the logger
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                # Return the path of the first file handler found
                if os.path.exists(handler.baseFilename):
                    return handler.baseFilename
        
        # If no file handler exists or the file doesn't exist, try to find a log file in standard locations
        # First check for current day's log in the default log directory
        log_dir, dir_writable = _ensure_log_directory()
        
        if dir_writable:
            # Primary log file in the standard location
            log_file_name = f"{name}-{datetime.now().strftime('%Y-%m-%d')}.log"
            log_file_path = Path(log_dir) / log_file_name
            
            if log_file_path.exists():
                return str(log_file_path)
            
            # If today's log doesn't exist, look for the most recent log file
            try:
                log_dir_path = Path(log_dir)
                if log_dir_path.exists() and log_dir_path.is_dir():
                    log_files = list(log_dir_path.glob(f"{name}-*.log"))
                    if log_files:
                        # Sort by modification time (most recent first)
                        log_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                        return str(log_files[0])
            except Exception:
                pass
        
        # Try fallback location
        fallback_path = Path.cwd() / f"{name}.log"
        if fallback_path.exists():
            return str(fallback_path)
        
        # Try temp directory
        temp_path = Path(tempfile.gettempdir()) / "version_finder" / "logs" / f"{name}.log"
        if temp_path.exists():
            return str(temp_path)
            
    except Exception:
        # If anything goes wrong, return None
        pass
    
    return None
