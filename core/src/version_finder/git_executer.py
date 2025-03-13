"""
git_executor.py
====================================
Module for handling git command execution logic.
"""
from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
import os
from typing import Optional, Union
from version_finder.logger import setup_logger
from version_finder.common import (
    DEFAULT_GIT_TIMEOUT,
    DEFAULT_GIT_MAX_RETRIES,
    DEFAULT_GIT_RETRY_DELAY,
    ENV_GIT_TIMEOUT,
    ENV_GIT_MAX_RETRIES,
    ENV_GIT_RETRY_DELAY
)


@dataclass
class GitConfig:
    """Configuration settings for git operations"""
    timeout: int = int(os.environ.get(ENV_GIT_TIMEOUT, str(DEFAULT_GIT_TIMEOUT)))
    max_retries: int = int(os.environ.get(ENV_GIT_MAX_RETRIES, str(DEFAULT_GIT_MAX_RETRIES)))
    retry_delay: int = int(os.environ.get(ENV_GIT_RETRY_DELAY, str(DEFAULT_GIT_RETRY_DELAY)))

    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.retry_delay <= 0:
            raise ValueError("retry_delay must be positive")


class GitCommandError(Exception):
    """Base exception for git command failures"""


class GitNetworkError(GitCommandError):
    """Raised when git operations fail due to network issues"""


class GitTimeoutError(GitCommandError):
    """Raised when git operations timeout"""


class GitPermissionError(GitCommandError):
    """Raised when git operations fail due to permission issues"""


class GitCommandExecutor:
    def __init__(self,
                 repository_path: Path,
                 config: Optional[GitConfig] = None):
        self.repository_path = repository_path
        self.config = config or GitConfig()
        self.logger = setup_logger()

        # Check Git is installed
        try:
            subprocess.check_output(["git", "--version"])
        except FileNotFoundError:
            raise GitCommandError("Git is not installed")

    def execute(self, command: list[str], retries: int = 0, check: bool = True) -> Union[bytes, subprocess.CompletedProcess]:
        """
        Execute a git command with retry logic and timeout.

        Args:
            command: Git command and arguments as list
            retries: Number of retries attempted so far
            check: Whether to check return code and raise on error

        Returns:
            Command output as bytes or CompletedProcess if check=False

        Raises:
            GitCommandError: Base exception for command failures
            GitNetworkError: When network-related errors occur
            GitTimeoutError: When command execution times out
            GitPermissionError: When permission issues occur
        """
        try:
            self.logger.debug(f"Executing git command: {' '.join(command)}")
            output = subprocess.check_output(
                ["git"] + command,
                cwd=self.repository_path,
                stderr=subprocess.PIPE,
                timeout=self.config.timeout
            )
            return output
        except subprocess.TimeoutExpired as e:
            if not check:
                return subprocess.CompletedProcess(args=["git"] + command, returncode=1, stdout=b"", stderr=str(e).encode())
            
            if retries < self.config.max_retries:
                self.logger.warning(f"Git command timed out, retrying in {self.config.retry_delay}s: {e}")
                time.sleep(self.config.retry_delay)
                return self.execute(command, retries + 1)
            
            raise GitTimeoutError(f"Git command timed out after {self.config.timeout}s: {' '.join(command)}") from e
            
        except subprocess.CalledProcessError as e:
            if not check:
                return e
                
            error_msg = e.stderr.decode('utf-8', errors='replace')
            
            # Handle specific error types
            if any(net_err in error_msg for net_err in ['could not resolve host', 'Connection refused', 'Connection timed out']):
                raise GitNetworkError(f"Network error during git operation: {error_msg}") from e
                
            if any(perm_err in error_msg for perm_err in ['Permission denied', 'authentication failed']):
                raise GitPermissionError(f"Permission error during git operation: {error_msg}") from e
                
            if retries < self.config.max_retries:
                self.logger.warning(f"Git command failed, retrying in {self.config.retry_delay}s: {error_msg}")
                time.sleep(self.config.retry_delay)
                return self.execute(command, retries + 1)
                
            raise GitCommandError(f"Git command failed: {error_msg}") from e
