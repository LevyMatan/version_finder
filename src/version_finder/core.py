"""
core.py
====================================
Core module for version_finder.
This module contains the core functionality for finding versions in a git repository.
It includes classes and functions for handling git operations and version finding.
The module is designed to work with git repositories and provides a user-friendly interface for
finding and comparing versions.
"""
from dataclasses import dataclass
from pathlib import Path
import os
import re
import subprocess
import time
from typing import List, Optional
from version_finder.protocols import LoggerProtocol, NullLogger


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


class GitError(Exception):
    """Base exception for git operations"""


class InvalidGitRepository(GitError):
    """Raised when the repository path is invalid"""


class GitCommandError(GitError):
    """Raised when a git command fails"""


class GitRepositoryNotClean(GitError):
    """Raised when the repository has uncommitted changes"""


class Commit:
    """A class to represent a git commit."""
    sha: str
    message: str
    author: str
    timestamp: int
    version: Optional[str] = None


class VersionFinder:
    """A class to handle git repository operations and version finding."""
    repository_path: Path
    submodules: List[str]
    branches: List[str]
    _has_remote: bool

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

    def __execute_git_command(self, command: List[str], retries: int = 0, check: bool = True) -> bytes:
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
            output = subprocess.check_output(
                ["git"] + command,
                cwd=self.repository_path,
                stderr=subprocess.PIPE,
                timeout=self.config.timeout
            )
            return output
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            if not check:
                # create a struct with returncode and set it to 1
                e.returncode = 1
                return e
            if retries < self.config.max_retries:
                self.logger.warning(f"Git command failed, retrying in {self.config.retry_delay}s: {e}")
                time.sleep(self.config.retry_delay)
                return self.__execute_git_command(command, retries + 1)
            raise GitCommandError(f"Git command failed: {e}") from e

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

            start_time = time.time()
            branch_pattern = re.compile(r'(?:remotes/origin/|\* |HEAD-> )')
            self.branches = sorted(set(
                branch_pattern.sub('', branch.strip())
                for branch in output.decode("utf-8").splitlines()
            ))
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

    def __extract_version_from_message(self, commit_message: str) -> Optional[str]:
        """
        Extract version from commit message using various patterns.

        Args:
            commit_message: The commit message to parse

        Returns:
            Optional[str]: Extracted version or None if no version found
        """
        # Pattern matches:
        # - Optional "Version: XX_" prefix
        # - Year (2014)
        # - Underscore or hyphen
        # - Numbers
        # - Optional "-" or "_" followed by additional numbers
        version_pattern = r'(?:Version:\s*(?:XX_)?)?(\d{4}(?:[_-]\d+)+(?:[_-]\d+)?)'

        match = re.search(version_pattern, commit_message)
        if match:
            return match.group(1)
        return None

    def __is_clean_git_repo(self) -> bool:
        """Check if the git repository is clean."""
        try:
            self.__execute_git_command(["diff", "--quiet", "HEAD"])
            return True
        except GitCommandError:
            return False

    def list_submodules(self) -> List[str]:
        """Get list of submodules."""
        return self.submodules

    def list_branches(self) -> List[str]:
        """Get list of branches."""
        return self.branches

    def has_branch(self, branch: str) -> bool:
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
        if not self.has_branch(branch):
            raise GitCommandError(f"Invalid branch: {branch}")

        try:
            self.__execute_git_command(["checkout", branch])
            if self._has_remote:
                self.__execute_git_command(["pull", "origin", branch])
            self.update_all_submodules()

        except GitCommandError as e:
            self.logger.error(f"Failed to update repository: {e}")
            raise

    def update_all_submodules(self) -> None:
        """Update submodules recursively."""
        try:
            self.__execute_git_command(["submodule", "update", "--init", "--recursive"])
        except GitCommandError as e:
            self.logger.error(f"Failed to update submodules: {e}")
            raise

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
        Find the nearest version commits before and after the given commit.

        Args:
            commit_sha: The commit SHA to get the surrounding version commits for.

        Returns:
            List containing the previous and next version commit SHAs. Elements can be None.
        """
        try:
            if not self.has_commit(commit_sha):
                raise GitCommandError(f"Commit {commit_sha} does not exist")

            # Find nearest version commits using grep
            prev_version = self.__execute_git_command([
                "log",
                "--grep=Version:",
                "--format=%H",
                "-n", "1",
                f"{commit_sha}~1"
            ]).decode("utf-8").strip() or None

            next_version = self.__execute_git_command([
                "log",
                "--grep=Version:",
                "--format=%H",
                "-n", "1",
                f"{commit_sha}^1..HEAD"
            ]).decode("utf-8").strip() or None

            return [prev_version, next_version]
        except GitCommandError as e:
            raise GitCommandError(f"Failed to get version commits: {e}") from e

    def get_version_from_commit(self, commit_sha: str) -> str:
        """
        Get the version from the commit message.

        Args:
            commit_sha: The commit SHA to get the version for.

        Returns:
            str: The version from the commit message.

        Raises:
            GitCommandError: If the commit does not exist or version cannot be extracted.
        """
        try:
            # Get the commit message using the pretty format
            output = self.__execute_git_command([
                "show",
                "-s",  # suppress diff output
                "--format=%s",  # get subject/title only
                commit_sha
            ])
            message = output.decode("utf-8").strip()

            # Extract version from message (assuming format "Version: X.Y.Z")
            version_string = self.__extract_version_from_message(message)
            if version_string:
                return version_string
            raise GitCommandError(f"Commit {commit_sha} does not contain version information")

        except GitCommandError as e:
            raise GitCommandError(f"Failed to get version for commit {commit_sha}: {e}") from e

    def has_commit(self, commit_sha: str) -> bool:
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

    def get_first_commit_including_submodule_changes(
            self, branch: str, submodule_path: str, submodule_target_commit: str) -> str:
        """
        Get the first commit that includes changes in the specified submodule.
        """
        # Update the repository to the specified branch
        self.update_repository(branch)

        # Verify submodule path exists
        if submodule_path not in self.submodules:
            raise GitCommandError(f"Invalid submodule path: {submodule_path}")

        # Get list of commits that touched submodule
        commits = self.__execute_git_command(
            ["log", "--format=%H", "--", submodule_path]).decode("utf-8").strip().split("\n")

        submodule_pointers = self.__execute_git_command([
            "ls-tree",
            "-r",
            "--full-tree",
            *commits,  # list of commit hashes
            submodule_path
        ]).decode("utf-8").strip().split("\n")

        # Each line will contain: "<mode> commit <submodule_hash> <submodule_path>"
        # Parse to get just the submodule hashes
        pointers = [line.split()[2] for line in submodule_pointers]

        # Apply binary search to find the first commit that points to an ancestor of the target commit
        left, right = 0, len(commits) - 1
        while left <= right:
            mid = (left + right) // 2
            submodule_ptr = pointers[mid]
            if self.__execute_git_command(
                    ["merge-base", "--is-ancestor", submodule_target_commit, submodule_ptr], check=False).returncode == 0:
                right = mid - 1
            else:
                left = mid + 1
        # If left is 0, it means the target commit is the first commit that includes changes in the submodule
        if left == 0:
            return commits[0]
        else:
            return commits[left - 1]

    def find_commit_by_version(self, branch: str, version: str) -> Optional[List[str]]:
        """
        Find the commit that indicates the specified version.
        """
        # Update the repository to the latest commit
        self.update_repository(branch)

        # Find the commit that indicates the specified version
        commits = self.__execute_git_command(
            ["log", "--grep", f"Version: {version}", "--format=%H"]).decode("utf-8").strip().split("\n")
        if not commits:
            return f"Version {version} not found"
        return commits

    def get_submodule_commit_hash(self, branch: str, commit: str, submodule: str) -> Optional[str]:
        """
        Get the submodule pointer from a commit.
        That is, get the hash of the submodule at the time of the commit.
        """
        # Update the repository to the latest commit
        if branch:
            self.update_repository(branch)

        if not self.has_commit(commit):
            self.logger.error(f"Commit {commit} does not exist")
            raise GitCommandError(f"Commit {commit} does not exist")

        # Get the submodule pointer from the commit
        submodule_ptr = self.__execute_git_command(
            ["ls-tree", "-r", "--full-tree", commit, submodule]).decode("utf-8").strip().split("\n")
        if not submodule_ptr:
            return None
        return submodule_ptr[0].split()[2]

    def get_commits_between_versions(self, branch: str, start_version: str,
                                     end_version: str, submodule: Optional[str] = None) -> List[str]:
        """
        Get the list of commits between two versions.
        """
        # Update the repository to the latest commit
        self.update_repository(branch)

        start_commit = self.find_commit_by_version(branch, start_version)
        end_commit = self.find_commit_by_version(branch, end_version)

        if submodule:
            first_submodule_pointer = self.get_submodule_commit_hash(start_commit, submodule, branch=branch)
            last_submodule_pointer = self.get_submodule_commit_hash(end_commit, submodule, branch=branch)
            if not first_submodule_pointer or not last_submodule_pointer:
                return []
            commits = self.__execute_git_command(
                ["log", "--format=%H", f"{first_submodule_pointer}..{last_submodule_pointer}"]).decode("utf-8").strip().split("\n")
        if not start_commit or not end_commit:
            return []

        # Get the list of commits between the two versions
        commits = self.__execute_git_command(
            ["log", "--format=%H", f"{start_commit}..{end_commit}"]).decode("utf-8").strip().split("\n")
        return commits

    def find_first_version_containing_commit(self, branch: str, commit_sha: str, submodule=None) -> Optional[str]:
        """
        Get the first version which includes the given commit.
        If submodule is provided, get the first version which includes the given commit in the submodule.
        If no version is found, return None.
        """

        # Update the repository to the latest commit
        self.update_repository(branch)

        if not self.has_commit(commit_sha):
            self.logger.error(f"Commit {commit_sha} does not exist")
            raise GitCommandError(f"Commit {commit_sha} does not exist")

        target_commit = commit_sha

        if submodule:
            # Get the first commit that includes changes in the submodule
            target_commit = self.get_first_commit_including_submodule_changes(branch, submodule, target_commit)

        versions_commits = self.get_commit_surrounding_versions(target_commit)
        if versions_commits is None or versions_commits[1] is None:
            return None

        return self.get_version_from_commit(versions_commits[1])
