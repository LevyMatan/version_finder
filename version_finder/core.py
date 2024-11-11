# version_finder/core.py
from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict

from .protocols import LoggerProtocol, NullLogger

@dataclass
class GitConfig:
    """Configuration settings for git operations"""
    timeout: int = 30
    max_retries: int = 0
    retry_delay: int = 1
    parallel_submodule_fetch: bool = True

class GitError(Exception):
    """Base exception for git operations"""
    pass

class InvalidGitRepository(GitError):
    """Raised when the repository path is invalid"""
    pass

class GitCommandError(GitError):
    """Raised when a git command fails"""
    pass

class GitRepositoryNotClean(GitError):
    """Raised when the repository has uncommitted changes"""
    pass

class VersionFinder:
    """A class to handle git repository operations and version finding."""

    def __init__(self,
                 path: Optional[str] = None,
                 config: Optional[GitConfig] = None,
                 logger: Optional[LoggerProtocol] = None) -> None:
        """
        Initialize the VersionFinder with a repository path and configuration.

        Args:
            path: Path to the git repository. Uses current directory if None.
            config: Configuration settings for git operations.
            logger: Logger instance for logging operations.
        """
        self.config = config or GitConfig()
        self.repository_path = Path(path or os.getcwd()).resolve()
        self.submodules: List[str] = []
        self.branches: List[str] = []
        self.logger = logger or NullLogger()  # Use NullLogger if no logger provided

        self.__validate_repository()
        self.__load_repository_info()

    def __validate_repository(self) -> None:
        """Validate the git repository and its state."""
        try:
            # Check if directory is a git repository by running git status
            self.__execute_git_command(["status"])
        except GitCommandError as e:
            # Convert GitCommandError to InvalidGitRepository
            raise InvalidGitRepository(f"Path {self.repository_path} is not a valid git repository: {str(e)}") from e

        if not self.__is_clean_git_repo():
            raise GitRepositoryNotClean("Repository has uncommitted changes")

    def __load_repository_info(self) -> None:
        """Load repository information including submodules and branches."""
        self.__load_submodules()
        self.__load_branches()

    def __execute_git_command(self, command: List[str], retries: int = 0) -> bytes:
        """
        Execute a git command with retry logic and timeout.

        Args:
            command: Git command and arguments as list.
            retries: Number of retries attempted so far.

        Returns:
            Command output as bytes.

        Raises:
            GitCommandError: If the command fails after all retries.
        """
        try:
            return subprocess.check_output(
                ["git"] + command,
                cwd=self.repository_path,
                stderr=subprocess.PIPE,
                timeout=self.config.timeout
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            if retries < self.config.max_retries:
                self.logger.warning(f"Git command failed, retrying in {self.config.retry_delay}s: {e}")
                time.sleep(self.config.retry_delay)
                return self.__execute_git_command(command, retries + 1)
            raise GitCommandError(f"Git command failed: {e}")

    def __load_submodules(self) -> None:
        """Load git submodules information."""
        try:
            output = self.__execute_git_command(["submodule", "status"])
            self.submodules = [line.split()[1] for line in output.decode("utf-8").splitlines()]
            self.logger.debug(f"Loaded submodules: {self.submodules}")
        except GitCommandError as e:
            self.logger.error(f"Failed to load submodules: {e}")
            self.submodules = []

    def __load_branches(self) -> None:
        """Load git branches information."""
        try:
            output = self.__execute_git_command(["branch", "-a"])
            self.logger.debug(f"Loaded branches output: {output}")
            self.branches = [
                branch.strip().replace('remotes/origin/', '')
                for branch in output.decode("utf-8").splitlines()
                if "->" not in branch or "*" not in branch
            ]
            self.branches = list(set(self.branches))
            self.logger.debug(f"Loaded branches: {self.branches}")
        except GitCommandError as e:
            self.logger.error(f"Failed to load branches: {e}")
            self.branches = []

    def __is_clean_git_repo(self) -> bool:
        """Check if the git repository is clean."""
        try:
            self.__execute_git_command(["diff", "--quiet", "HEAD"])
            return True
        except GitCommandError:
            return False

    def get_submodules(self) -> List[str]:
        """Get list of submodules."""
        return self.submodules

    def get_branches(self) -> List[str]:
        """Get list of branches."""
        return self.branches

    def is_valid_branch(self, branch: str) -> bool:
        """Check if a branch exists."""
        return branch in self.branches

    def update_repository(self, branch: str) -> None:
        """
        Update the repository and its submodules to the specified branch.

        Args:
            branch: Branch name to checkout.

        Raises:
            GitCommandError: If update operations fail.
        """
        if not self.is_valid_branch(branch):
            raise GitCommandError(f"Invalid branch: {branch}")

        try:
            self.__execute_git_command(["checkout", branch])
            self.__execute_git_command(["pull", "origin", branch])

            if self.config.parallel_submodule_fetch and self.submodules:
                self.__update_submodules_parallel()
            else:
                self.__execute_git_command(["submodule", "update", "--init", "--recursive"])

        except GitCommandError as e:
            self.logger.error(f"Failed to update repository: {e}")
            raise

    def __update_submodules_parallel(self) -> None:
        """Update submodules in parallel using ThreadPoolExecutor."""
        def update_submodule(submodule: str) -> None:
            try:
                self.__execute_git_command(["submodule", "update", "--init", "--recursive", submodule])
            except GitCommandError as e:
                self.logger.error(f"Failed to update submodule {submodule}: {e}")
                raise

        with ThreadPoolExecutor() as executor:
            # Submit all submodule update tasks
            futures = [executor.submit(update_submodule, submodule) for submodule in self.submodules]

            # Wait for all tasks to complete
            for future in futures:
                future.result(timeout=self.config.timeout)
    def verify_commit_signature(self, commit_sha: str) -> bool:
        try:
            self.__execute_git_command(["verify-commit", commit_sha])
            return True
        except GitCommandError:
            return False

    def get_commit_info(self, commit_sha: str) -> Dict[str, str]:
        """
        Get detailed information about a commit.

        Args:
            commit_sha: The commit SHA to inspect.

        Returns:
            Dictionary containing commit information.
        """
        if not self.verify_commit_signature(commit_sha):
            raise GitCommandError(f"Invalid commit signature: {commit_sha}")
        try:
            output = self.__execute_git_command(["show", "-s", "--format=%H%n%an%n%ae%n%at%n%s", commit_sha])
            hash_, author, email, timestamp, subject = output.decode("utf-8").strip().split("\n")
            return {
                "hash": hash_,
                "author": author,
                "email": email,
                "timestamp": timestamp,
                "subject": subject
            }
        except GitCommandError as e:
            self.logger.error(f"Failed to get commit info for {commit_sha}: {e}")
            raise
