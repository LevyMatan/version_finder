# version_finder/core.py
from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Any

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

    def __has_remote(self) -> bool:
        """Check if the repository has any remotes configured."""
        try:
            output = self.__execute_git_command(["remote"])
            return bool(output.strip())
        except GitCommandError:
            return False

    def __validate_repository(self) -> None:
        """Validate the git repository and its state."""
        try:
            # Check if directory is a git repository by running git status
            self.__execute_git_command(["status"])
        except GitCommandError as e:
            # Convert GitCommandError to InvalidGitRepository
            raise InvalidGitRepository(f"Path {self.repository_path} is not a valid git repository: {str(e)}") from e

        # Store remote status
        self._has_remote = self.__has_remote()
        self.logger.debug(f"Repository has remote: {self._has_remote}")

        if not self.__is_clean_git_repo():
            raise GitRepositoryNotClean("Repository has uncommitted changes")

    def __load_repository_info(self) -> None:
        """Load repository information including submodules and branches."""
        if self._has_remote:
            self.logger.info(f"Fetching latest changes from remote repository: {self.repository_path}")
            self.__fetch_repository()
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

    def __fetch_repository(self) -> None:
        """Fetch latest changes from remote repository."""
        try:
            output = self.__execute_git_command(["fetch", "--all"])
            self.logger.debug(f"Fetch output: {output}")
        except GitCommandError as e:
            self.logger.error(f"Failed to fetch repository: {e}")

    def __load_branches(self) -> None:
        """Load git branches information."""
        try:
            output = self.__execute_git_command(["branch", "-a"])
            self.logger.debug(f"Loaded branches output: {output}")
            # TODO: Might wish to optimize the branch filtering
            # Time how long it takes to filter the branch output in mili-seconds
            start_time = time.time()
            self.branches = [
                branch.strip().replace('remotes/origin/', '').replace('* ', '').replace('HEAD-> ', '')
                for branch in output.decode("utf-8").splitlines()
            ]
            filtering_time = time.time()
            self.branches = list(set(self.branches))
            remove_duplicates_time = time.time()
            self.branches.sort()
            sort_time = time.time()
            self.logger.debug(f"Branch filtering took {filtering_time - start_time} seconds")
            self.logger.debug(f"Removing duplicates took {remove_duplicates_time - filtering_time} seconds")
            self.logger.debug(f"Sorting took {sort_time - remove_duplicates_time} seconds")
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
            if self._has_remote:
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

    def find_commits_by_text(self, branch: str, text: str) -> List[str]:
        """
        Find commits in the specified branch that contain the given text in either title or description.

        Args:
            branch: Branch name to search.
            text: Text to search for in commit messages (title and description).

        Returns:
            List of commit hashes.

        Raises:
            GitCommandError: If the git command fails.
        """
        try:
            self.logger.debug(f"Finding commits by text: {text} in branch: {branch}")
            # Use --format to get hash, subject and body in one command
            # %H: commit hash
            # %s: subject (title)
            # %b: body (description)
            # Using ASCII delimiter (0x1F) to separate fields
            output = self.__execute_git_command([
                "log",
                "--format=%H%x1F%s%x1F%b",
                branch
            ])

            commits = output.decode("utf-8").strip().split("\n")
            matching_commits = []

            for commit in commits:
                if not commit:  # Skip empty lines
                    continue
                # Split the commit info using the ASCII delimiter
                commit_parts = commit.split("\x1F")
                if len(commit_parts) >= 3:
                    commit_hash, subject, body = commit_parts
                    # Search in both subject and body
                    if (text.lower() in subject.lower() or
                            text.lower() in body.lower()):
                        matching_commits.append(commit_hash)

            return matching_commits
        except GitCommandError as e:
            self.logger.error(f"Failed to find commits by text: {e}")
            raise

    def get_commit_surrounding_versions(self, commit_sha: str) -> List[Optional[str]]:
        """
        Get the commit SHA of the previous and next commits.

        Args:
            commit_sha: The commit SHA to get the surrounding versions for.

        Returns:
            List containing the previous and next commit SHAs.
        """
        try:
            # Get the parent commit of the given commit
            parent_commit = self.__execute_git_command(["rev-list", "--parents", "-n", "1", commit_sha])
            parent_commit = parent_commit.decode("utf-8").strip().split(" ")[1]

            # Get the list of commits in the current branch
            commits = self.__execute_git_command(["rev-list", "HEAD"])
            commits = commits.decode("utf-8").strip().split("\n")

            # Find the index of the given commit in the list
            commit_index = commits.index(commit_sha)

            # Get the previous and next commits
            previous_commit = commits[commit_index + 1] if commit_index > 0 else None
            next_commit = commits[commit_index - 1] if commit_index < len(commits) - 1 else None

            return [previous_commit, next_commit]
        except GitCommandError as e:
            raise GitCommandError(f"Failed to get commit surrounding versions: {e}") from e

    def commit_exists(self, commit_sha: str) -> bool:
        """
        Check if a commit exists in the repository.

        Args:
            commit_sha: The commit SHA to check.

        Returns:
            bool: True if the commit exists, False otherwise.
        """
        try:
            # -e flag just checks for existence, -t type check is also good
            self.__execute_git_command(["cat-file", "-e", commit_sha])
            return True
        except GitCommandError:
            return False

    def check_commit(self, commit_sha: str) -> Dict[str, Any]:
        """
        Check if a commit exists and get its type.

        Args:
            commit_sha: The commit SHA to check.

        Returns:
            Dict containing:
                - exists (bool): Whether the object exists
                - type (str): Type of the object (if it exists)
                - error (str): Error message (if check failed)
        """
        try:
            # -t returns the type of the object
            output = self.__execute_git_command(["cat-file", "-t", commit_sha])
            return {
                "exists": True,
                "type": output.decode("utf-8").strip(),
                "error": None
            }
        except GitCommandError as e:
            return {
                "exists": False,
                "type": None,
                "error": str(e)
            }

    def verify_commit_signature(self, commit_sha: str) -> bool:
        """
        Verify the GPG signature of a git commit.

        Args:
            commit_sha: The commit SHA to verify.

        Returns:
            bool: True if signature is valid, False otherwise.
        """
        try:
            output = self.__execute_git_command(["verify-commit", "--raw", commit_sha])
            return {
                "verified": True,
                "status": "valid",
                "raw_output": output.decode("utf-8")
            }
        except GitCommandError as e:
            return {
                "verified": False,
                "status": "invalid",
                "error": str(e)
            }

    def get_commit_info(self, commit_sha: str) -> Dict[str, str]:
        """
        Get detailed information about a commit.

        Args:
            commit_sha: The commit SHA to inspect.

        Returns:
            Dictionary containing commit information.
        """
        if not self.commit_exists(commit_sha):
            raise GitCommandError(f"Invalid commit: {commit_sha}")
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
