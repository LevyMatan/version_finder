"""
git_executor.py
====================================
Module for handling git command execution logic.
"""
from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
from typing import Optional
from .protocols import LoggerProtocol, NullLogger


@dataclass
class GitConfig:
    """Configuration settings for git operations"""
    timeout: int = 30
    max_retries: int = 0
    retry_delay: int = 1

    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.retry_delay <= 0:
            raise ValueError("retry_delay must be positive")


class GitCommandError(Exception):
    """Raised when a git command fails"""


class GitCommandExecutor:
    def __init__(self,
                 repository_path: Path,
                 config: Optional[GitConfig] = None,
                 logger: Optional[LoggerProtocol] = None):
        self.repository_path = repository_path
        self.config = config or GitConfig()
        self.logger = logger or NullLogger()

        # Check Git is installed
        try:
            subprocess.check_output(["git", "--version"])
        except FileNotFoundError:
            raise GitCommandError("Git is not installed")

    def execute(self, command: list[str], retries: int = 0, check: bool = True) -> bytes:
        """
        Execute a git command with retry logic and timeout.

        Args:
            command: Git command and arguments as list
            retries: Number of retries attempted so far
            check: Whether to check return code and raise on error

        Returns:
            Command output as bytes

        Raises:
            GitCommandError: If the command fails after all retries
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
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            if not check:
                e.returncode = 1
                return e
            if retries < self.config.max_retries:
                self.logger.warning(f"Git command failed, retrying in {self.config.retry_delay}s: {e}")
                time.sleep(self.config.retry_delay)
                return self.execute(command, retries + 1)
            raise GitCommandError(f"Git command failed: {e}") from e
