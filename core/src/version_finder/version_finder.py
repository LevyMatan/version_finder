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
import difflib
import os
import re
import time
from typing import List, Optional, Dict, Callable
from version_finder.git_executer import GitCommandExecutor, GitConfig, GitCommandError
from version_finder.logger import setup_logger
from version_finder.common import GIT_CMD_FETCH, GIT_CMD_CHECKOUT, GIT_CMD_SUBMODULE_UPDATE, GIT_CMD_LIST_BRANCHES, GIT_CMD_LIST_SUBMODULES, BRANCH_PATTERN, SUBMODULE_PATTERN


class GitError(Exception):
    """Base exception for git operations"""


class InvalidGitRepository(GitError):
    """Raised when the repository path is invalid"""


class GitRepositoryNotClean(GitError):
    """Raised when the repository has uncommitted changes"""


class InvalidCommitError(GitError):
    """Raised when the commit is invalid"""


class InvalidSubmoduleError(GitError):
    """Raised when the submodule is invalid"""


class InvalidBranchError(GitError):
    """Raised when the branch is invalid"""


class VersionNotFoundError(GitError):
    """Raised when version is not found in commits message"""

class InvalidFilepathError(GitError):
    """Raised when a filepath input is not valid"""


class GitNotInstalledError(GitError):
    """Raised when git is not installed"""

    def __init__(self, message: str):
        installation_guide = """
        To use version_finder, you need git installed on your system.

        Installation instructions:
        - macOS: Install via Xcode Command Line Tools with 'xcode-select --install'
        - Linux: Use your package manager e.g. 'apt install git' or 'yum install git'
        - Windows: Download from https://git-scm.com/download/win

        After installation, ensure 'git' is available in your system PATH.
        """
        super().__init__(f"{message}\n{installation_guide}")


class RepositoryNotTaskReady(GitError):
    """Raised when the repository is not ready for task"""

    def __init__(self):
        super().__init__("Please run update_repository(<selected_branch>) first.")


@dataclass
class Commit:
    """A class to represent a git commit."""
    sha: str
    subject: str
    message: str
    author: str
    timestamp: int
    version: Optional[str] = None

    def __repr__(self):
        return f"Commit(sha={self.sha}    subject={self.subject})"

    def __str__(self):
        return f"{self.sha}    {self.subject}"


@dataclass
class VersionFinderTask:
    """A class to represent a VersionFinder task."""
    index: int
    name: str
    description: str
    args: Optional[Dict] = None
    run: Callable = None


class VersionFinderTaskRegistry:
    def __init__(self):
        self._tasks_by_name: Dict[str, VersionFinderTask] = {}
        self._tasks_by_index: Dict[int, VersionFinderTask] = {}
        self._initialize_tasks()

    def _initialize_tasks(self):
        tasks = [
            VersionFinderTask(
                name="Find first version containing commit",
                index=0,
                description="""The most common task is to find the first version that includes a change (=commit).
                             Given a commit SHA identifier in a repository, it can be done easily using: `git log --grep=version: <commit_ha>^1..<HEAD>` you now what to scroll down all the way to find the first commit.
                             But, when the change is part of a submodule, things can can a little more tricky. Given a submodule with the reposity and the commit SHA identifier, Version Finder
                             will iterate over all the commits that change the submodule pointer. It will than apply binary search to find the first ancestor of the change.""",
            ),
            VersionFinderTask(
                name="Find all commits between two versions",
                index=1,
                description="""Trying to identify a commit that may cause an issue, a user would like to seek all the changes between two versions.
                Once again an easy solution is `git log <old_version_tag>..<new_version_tag>`. If a submodule is given than Version Finder will get the submodule pointers at each commit, and log all the commits between them.""",
            ),
            VersionFinderTask(
                name="Find commit by text",
                index=2,
                description="An helper task in-order to identify the correct commit SHA identifier for later",
            )
        ]

        for task in tasks:
            self._tasks_by_name[task.name] = task
            self._tasks_by_index[task.index] = task

    def get_by_name(self, name: str) -> Optional[VersionFinderTask]:
        return self._tasks_by_name.get(name)

    def get_by_index(self, index: int) -> Optional[VersionFinderTask]:
        return self._tasks_by_index.get(index)

    def get_tasks_by_index(self) -> list[VersionFinderTask]:
        """Returns tasks sorted by index"""
        return [self._tasks_by_index[i] for i in sorted(self._tasks_by_index.keys())]

    def has_index(self, index: int) -> bool:
        return index in self._tasks_by_index

    def has_name(self, name: str) -> bool:
        return name in self._tasks_by_name

    def _set_task_action(self, index: int, action: Callable):
        task = self.get_by_index(index)
        if task:
            task.run = action
        else:
            raise ValueError(f"Task with index {index} not found")

    def _set_task_action_params(self, index: int, params: Dict):
        task = self.get_by_index(index)
        if task:
            task.args = params
        else:
            raise ValueError(f"Task with index {index} not found")

    def initialize_actions_and_args(self, actions: Dict[int, Callable], params: Dict[int, List[str]]):
        """

        """
        for index, action in actions.items():
            self._set_task_action(index, action)
            self._set_task_action_params(index, params[index])


class VersionFinder:
    """A class to handle git repository operations and version finding."""
    repository_path: Path
    submodules: List[str]
    branches: List[str]
    _has_remote: bool

    # Consolidated version pattern that handles various formats:
    # - Optional prefixes like "Version:", "VERSION:", "Updated version"
    # - Optional "XX_" prefix in the version number
    # - Year formats (e.g., 2023)
    # - Various separators (., _, -)
    # - Multiple version components (e.g., 1.2.3, 2023_01_15, etc.)
    # 
    # Examples of matched versions:
    # - Version: 1.2.3
    # - VERSION: XX_2023_01_15
    # - Updated version 4.5-2
    # - 2023.01.15
    version_pattern = r"(?:(?:Version|VERSION|Updated version)s*:?\s*|[^a-zA-Z0-9][^0-9\s]*)?(?:XX_)?(\d{1,4}(?:[._-]\d+)+)"

    # Pattern used specifically for git grep searches
    git_regex_pattern_for_version = "(Version|VERSION|Updated version)(:)? (XX_)?[0-9]+([._-][0-9]+)+"

    def __init__(self,
                 path: str = '',
                 config: Optional[GitConfig] = None) -> None:
        """
        Initialize the VersionFinder with a repository path and configuration.

        Args:
            path: Path to the git repository. Uses current directory if None.
            config: Configuration settings for git operations.
        """
        self.config = config or GitConfig()
        self.repository_path = Path(path or os.getcwd()).resolve()
        self.logger = setup_logger()
        self.updated_branch: str = ''

        try:
            self._git = GitCommandExecutor(self.repository_path, self.config)
        except GitCommandError as e:
            self.logger.error(f"Error: {e}")
            raise GitNotInstalledError(e)

        self.is_task_ready = False
        self.submodules: List[str] = []
        self.branches: List[str] = []

        self.__validate_repository()
        self.__load_repository_info()

    def __has_remote(self) -> bool:
        """Check if the repository has any remotes configured."""
        try:
            output: bytes = self._git.execute(["remote"])
            return bool(output.strip())
        except GitCommandError:
            return False

    def __validate_repository(self) -> None:
        """Validate the git repository and its state."""
        try:
            # Check if directory is a git repository by running git status
            self._git.execute(["status"])
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
        self.__load_branches()
        self.__load_submodules()
        # If the checked out branch is valid, set it as updated
        self.updated_branch = self.get_current_branch()

    def __load_submodules(self) -> None:
        """Load git submodules information."""
        try:
            output = self._git.execute(["submodule", "status"])
            self.submodules = [line.split()[1] for line in output.decode("utf-8").splitlines()]
            self.logger.debug(f"Loaded submodules: {self.submodules}")
        except GitCommandError as e:
            self.logger.error(f"Failed to load submodules: {e}")
            self.submodules = []

    def __fetch_repository(self) -> None:
        """Fetch latest changes from remote repository."""
        try:
            output = self._git.execute(["fetch", "--all"])
            self.logger.debug(f"Fetch output: {output}")
        except GitCommandError as e:
            self.logger.error(f"Failed to fetch repository: {e}")

    def __load_branches(self) -> None:
        """Load git branches information."""
        try:
            output = self._git.execute(["branch", "-a"])
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

        match = re.search(self.version_pattern, commit_message)
        if match:
            self.logger.debug(f"match.group(0) = {match.group(0)}")
            return match.group(1)
        return None

    def __is_clean_git_repo(self) -> bool:
        """Check if the git repository is clean."""
        try:
            self._git.execute(["diff", "--quiet", "HEAD"])
            return True
        except GitCommandError:
            return False

    def list_submodules(self) -> List[str]:
        """Get list of submodules."""
        return self.submodules

    def list_branches(self) -> List[str]:
        """Get list of branches."""
        return self.branches

    def get_commit_info(self, commit_sha: str, submodule: str = '') -> Commit:
        """Get detailed commit information."""

        # Verify ready for Tasks
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        git_command = ["show", "-s", "--format=%H%x1F%s%x1F%B%x1F%an%x1F%at", commit_sha]
        if submodule:
            git_command.insert(0, "--git-dir")
            git_command.insert(1, f"{submodule}/.git")
        try:
            output = self._git.execute(git_command).decode("utf-8").strip()
        except GitCommandError as e:
            raise InvalidCommitError(f"Failed to get commit info: {e}")
        self.logger.debug(f"Commit info output: {output}")
        output = output.split('\x1F')
        for elemetn in output:
            self.logger.debug(f"Element: {elemetn}")
        self.logger.debug(f"The length of output is: {len(output)}")
        sha, subject, message, author, timestamp = output
        version = self.__extract_version_from_message(message)

        return Commit(
            sha=sha,
            subject=subject,
            message=message,
            author=author,
            timestamp=int(timestamp),
            version=version
        )

    def get_current_branch(self) -> str:
        """Get the current Git branch name.

        Returns:
            str: The name of the current branch if successfully determined.
                Returns None if:
                - The repository is in a detached HEAD state
                - There was an error executing the git command
                - The branch name could not be determined

        Raises:
            GitCommandError: May be raised during git command execution, but is caught internally
        """
        current_branch = None
        try:
            output = self._git.execute(["rev-parse", "--abbrev-ref", "HEAD"])
            output = output.decode("utf-8").strip()
            self.logger.debug(f"Current branch output: {output}")
            if output not in ["HEAD"]:
                current_branch = output
        except GitCommandError as e:
            self.logger.error(f"Failed to get current branch: {e}")
        return current_branch

    def has_branch(self, branch: str) -> bool:
        """Check if a branch exists."""
        return branch in self.branches

    def update_repository(self, branch: str) -> None:
        """
        Update the repository to the specified branch.

        Args:
            branch: Branch name to checkout

        Raises:
            InvalidBranchError: If the branch is invalid
            GitRepositoryNotClean: If the repository has uncommitted changes
        """
        self.logger.info(f"Updating repository to branch: {branch}")

        # Fetch latest changes
        try:
            self._git.execute(GIT_CMD_FETCH)
        except GitCommandError as e:
            self.logger.error(f"Failed to fetch: {e}")
            raise

        # Check if branch exists
        branches = self.get_branches()
        if branch not in branches:
            raise InvalidBranchError(f"Branch '{branch}' not found in repository")

        # Checkout branch
        try:
            self._git.execute(GIT_CMD_CHECKOUT + [branch])
        except GitCommandError as e:
            self.logger.error(f"Failed to checkout branch {branch}: {e}")
            raise

        # Update submodules
        try:
            self._git.execute(GIT_CMD_SUBMODULE_UPDATE)
        except GitCommandError as e:
            self.logger.warning(f"Failed to update submodules: {e}")
            # Continue anyway, as this might not be critical

        self.logger.info(f"Repository updated to branch: {branch}")

    def get_branches(self) -> List[str]:
        """
        Get list of branches in the repository.

        Returns:
            List of branch names
        """
        try:
            output = self._git.execute(GIT_CMD_LIST_BRANCHES)
            branches = []
            for line in output.decode('utf-8').splitlines():
                match = re.match(BRANCH_PATTERN, line.strip())
                if match:
                    branch = match.group(1)
                    # Remove remote prefix if present
                    if branch.startswith('remotes/'):
                        parts = branch.split('/', 2)
                        if len(parts) > 2:
                            branch = parts[2]
                    branches.append(branch)
            return sorted(list(set(branches)))  # Remove duplicates and sort
        except GitCommandError as e:
            self.logger.error(f"Failed to get branches: {e}")
            return []

    def get_submodules(self) -> List[str]:
        """
        Get list of submodules in the repository.

        Returns:
            List of submodule names
        """
        try:
            output = self._git.execute(GIT_CMD_LIST_SUBMODULES)
            submodules = []
            for line in output.decode('utf-8').splitlines():
                match = re.match(SUBMODULE_PATTERN, line.strip())
                if match:
                    submodule = match.group(2)
                    submodules.append(submodule)
            return sorted(submodules)
        except GitCommandError as e:
            self.logger.error(f"Failed to get submodules: {e}")
            return []

    def find_commits_by_text(self, text: str, submodule: str = '') -> List[Commit]:
        """
        Find commits in the specified branch that contain the given text in either title or description.

        Args:
            text: Text to search for in commit messages (title and description).
            submodule: Optional submodule path to search in.

        Returns:
            List of commit hashes.

        Raises:
            GitCommandError: If the git command fails.
        """
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        try:
            command = [
                "log",
                "--format=%H%x1F%s%x1F%b"
            ]

            if submodule:
                # Verify submodule exists
                if submodule not in self.submodules:
                    raise InvalidSubmoduleError(f"Invalid submodule path: {submodule}")
                # Execute command in submodule directory
                command.insert(0, "-C")
                command.insert(1, submodule)

            output = self._git.execute(command)
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

            return [self.get_commit_info(commit_sha, submodule=submodule) for commit_sha in matching_commits]
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
            prev_version = self._git.execute([
                "log",
                f"--grep={self.git_regex_pattern_for_version}",
                "--extended-regexp",
                "--format=%H",
                "-n", "1",
                f"{commit_sha}~1"
            ]).decode("utf-8").strip() or None

            # Add validation for empty output
            if not prev_version:
                self.logger.debug("No previous version found")

            next_version_output = self._git.execute([
                "log",
                f"--grep={self.git_regex_pattern_for_version}",
                "--extended-regexp",
                "--format=%H",
                f"{commit_sha}^1..HEAD"
            ]).decode("utf-8").strip()

            # Add validation for empty output
            next_version = next_version_output.split()[-1] if next_version_output else None
            if not next_version:
                self.logger.debug("No next version found")

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
            output = self._git.execute([
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
            self._git.execute(["cat-file", "-e", commit_sha])
            return True
        except GitCommandError:
            return False

    def submodule_has_commit(self, submodule_path: str, commit_sha: str) -> bool:
        """
        Check if a commit exists in a submodule.

        Args:
            submodule_path: The path to the submodule.
            commit_sha: The commit SHA to check.

        Returns:
            bool: True if the commit exists in the submodule, False otherwise.
        """
        try:
            # Check if the commit exists in the submodule
            self._git.execute(["-C", submodule_path, "cat-file", "-e", commit_sha])
            return True
        except GitCommandError:
            self.logger.error(f"Commit {commit_sha} does not exist in submodule {submodule_path}")
            return False

    def get_first_commit_including_submodule_changes(
            self, submodule_path: str, submodule_target_commit: str) -> str:
        """
        Get the first commit that includes changes in the specified submodule.
        """
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        # Verify submodule path exists
        if submodule_path not in self.submodules:
            raise GitCommandError(f"Invalid submodule path: {submodule_path}")

        # Verify commit exists in submodule
        if not self.submodule_has_commit(submodule_path, submodule_target_commit):
            raise GitCommandError(f"Commit {submodule_target_commit} does not exist in submodule {submodule_path}")

        def parse_git_log_output(git_log_output):
            repo_commit_sha = None
            tuples = []
            for line in git_log_output.splitlines():
                # Detect commit lines
                if line.startswith("Commit: "):
                    repo_commit_sha = line.split()[1]
                # Detect submodule commit change lines
                match = re.match(r"^\+Subproject commit (\w+)", line)
                if match and repo_commit_sha:
                    submodule_commit_sha = match.group(1)
                    tuples.append((repo_commit_sha, submodule_commit_sha))
                    repo_commit_sha = None  # Reset to avoid duplication
            return tuples

        git_log_output = self.__get_commits_changing_submodule_pointers_and_the_new_pointer(submodule_path, 1500)
        if not git_log_output:
            raise GitCommandError(f"No commits found that change submodule {submodule_path} or its ancestors")
        # Parse the git log output
        repo_commot_submodule_ptr_tuples = parse_git_log_output(git_log_output)
        self.logger.debug(
            f"Found {len(repo_commot_submodule_ptr_tuples)} commits that change submodule {submodule_path}")
        self.logger.debug(f"First commit: {repo_commot_submodule_ptr_tuples[0][0]}")
        self.logger.debug(f"Last commit: {repo_commot_submodule_ptr_tuples[-1][0]}")

        # Apply binary search to find the first commit that points to an ancestor of the target commit
        left, right = 0, len(repo_commot_submodule_ptr_tuples) - 1
        while left <= right:
            mid = (left + right) // 2
            submodule_ptr = repo_commot_submodule_ptr_tuples[mid][1]
            self.logger.debug(f"Binary search - Left: {left}, Right: {right}, Mid: {mid}")
            self.logger.debug(f"Checking if {submodule_target_commit} is ancestor of {submodule_ptr}")

            is_ancestor = self._git.execute(
                ["-C", submodule_path, "merge-base", "--is-ancestor", submodule_target_commit, submodule_ptr],
                check=False) == b''
            self.logger.debug(f"Is ancestor: {is_ancestor}")
            is_equal = submodule_target_commit == submodule_ptr
            self.logger.debug(f"Is equal: {is_equal}")
            is_ancestor_or_equal = is_ancestor or is_equal
            self.logger.debug(f"Is ancestor or equal result: {is_ancestor_or_equal}")

            if is_ancestor_or_equal:
                self.logger.debug(f"Moving left pointer from {left} to {mid + 1}")
                left = mid + 1
            else:
                self.logger.debug(f"Moving right pointer from {right} to {mid - 1}")
                right = mid - 1

        self.logger.debug(f"Binary search completed - Final left: {left}, Final right: {right}")

        first_commit_to_include_submodule_change = repo_commot_submodule_ptr_tuples[right][0]
        self.logger.debug(f"First commit that includes submodule change: {first_commit_to_include_submodule_change}")
        return first_commit_to_include_submodule_change

    def __get_commits_changing_submodule_pointers_and_the_new_pointer(self, submodule_path, commit_num_limit):
        git_log_command = [
            "log", "--format=Commit: %H", "-p", "--", submodule_path,
        ]
        if commit_num_limit:
            git_log_command.insert(2, f"-n {commit_num_limit}")
        git_log_output = self._git.execute(git_log_command).decode("utf-8").strip()
        return git_log_output

    def find_commit_by_version(self, version: str) -> List[str]:
        """
        Find the commit that indicates the specified version.
        """
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        # Find the commit that indicates the specified version
        commits = self._git.execute(
            ["log", "-i", "--grep", version, "--format=%H"]).decode("utf-8").strip().split("\n")
        self.logger.debug(f"Found {len(commits)} commits for version {version}")
        self.logger.debug(f"The type of commits: {type(commits)}")
        return commits

    def get_submodule_commit_hash(self, commit: str, submodule: str) -> Optional[str]:
        """
        Get the submodule pointer from a commit.
        That is, get the hash of the submodule at the time of the commit.
        """
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        if not self.has_commit(commit):
            self.logger.error(f"Commit {commit} does not exist")
            raise GitCommandError(f"Commit {commit} does not exist")

        # Get the submodule pointer from the commit
        submodule_ptr = self._git.execute(
            ["ls-tree", "-r", "--full-tree", commit, submodule]).decode("utf-8").strip().split("\n")
        if not submodule_ptr:
            return None
        return submodule_ptr[0].split()[2]

    def get_commits_between_versions(self, start_version: str,
                                     end_version: str, submodule: Optional[str] = None) -> List[Commit]:
        """
        Get the list of commits between two versions.
        """
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        start_commit = self.find_commit_by_version(start_version)[0]
        self.logger.debug(f"The commit SHA of version: {start_version} is {start_commit}")
        if not start_commit:
            raise VersionNotFoundError(f"Version: {start_version} was not found in the repository.")
        end_commit = self.find_commit_by_version(end_version)[0]
        self.logger.debug(f"The commit SHA of version: {end_version} is {end_commit}")
        if not end_commit:
            raise VersionNotFoundError(f"Version: {end_version} was not found in the repository.")

        if submodule:
            start_commit = self.get_submodule_commit_hash(start_commit, submodule)
            self.logger.debug(f"Version {start_version} point to submodule {submodule} commit: {start_commit}")
            if not start_commit:
                raise GitError(f"startversion:start_commit: Couldn't find the pointer to submodule: {submodule}")
            end_commit = self.get_submodule_commit_hash(end_commit, submodule)
            self.logger.debug(f"Version {end_version} point to submodule {submodule} commit: {end_commit}")
            if not end_commit:
                raise GitError(f"startversion:end_commit: Couldn't find the pointer to submodule: {submodule}")

        lower_bound_commit = self.get_parent_commit(start_commit, submodule)
        git_command = ["log", "--format=%H", f"{lower_bound_commit}..{end_commit}"]
        if submodule:
            git_command.insert(0, "-C")
            git_command.insert(1, submodule)

        try:
            commit_sha_list = self._git.execute(
                git_command).decode("utf-8").strip().split("\n")
        except GitCommandError as e:
            self.logger.error(f"Failed to get commits between versions: {e}")
            raise e

        return [self.get_commit_info(commit, submodule=submodule) for commit in commit_sha_list]

    def get_parent_commit(self, commit: str, submodule=None) -> str:
        """
        Get the parent commit of a given commit hash.

        Args:
            commit: The commit hash to find the parent for
            submodule: Optional submodule path to look in

        Returns:
            str: Parent commit hash, or original commit if no parent exists

        Raises:
            RepositoryNotTaskReady: If repository is not ready
        """
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()
        if submodule:
            if self.submodule_has_commit(submodule, f"{commit}^"):
                return f"{commit}^"
            return commit
        if self.has_commit(f"{commit}^"):
            return f"{commit}^"
        return commit

    def find_first_version_containing_commit(self, commit_sha: str, submodule=None) -> Optional[str]:
        """
        Get the first version which includes the given commit.
        If submodule is provided, get the first version which includes the given commit in the submodule.
        If no version is found, return None.
        """

        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        if submodule:
            # Get the first commit that includes changes in the submodule
            commit_sha = self.get_first_commit_including_submodule_changes(submodule, commit_sha)

        if not self.has_commit(commit_sha):
            self.logger.error(f"Commit {commit_sha} does not exist")
            raise InvalidCommitError(f"Commit {commit_sha} does not exist in the repository: {self.repository_path}")

        versions_commits = self.get_commit_surrounding_versions(commit_sha)
        if versions_commits is None or versions_commits[1] is None:
            return None

        return self.get_version_from_commit(versions_commits[1])

    def get_commit_sha_from_relative_string(self, relative_string: str, submodule: str = '') -> Optional[str]:
        """
        Get the commit SHA from a relative string.
        For example, "HEAD~1" will return the SHA of the commit that is one commit before HEAD.
        """
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()

        # Get the commit SHA from the relative string
        try:
            commit_sha = self._git.execute(
                ["rev-parse", relative_string]).decode("utf-8").strip()
        except GitCommandError as e:
            self.logger.error(f"Error while getting commit SHA from relative string: {e}")
            raise InvalidCommitError(f"Invalid commit SHA: {e}")
        return commit_sha

    def get_task_api_functions(self) -> Dict[int, Callable]:
        """
        Get the list of API functions.
        """
        return {
            0: self.find_commits_by_text,
            1: self.find_first_version_containing_commit,
            2: self.get_commits_between_versions,
        }

    def get_task_api_functions_params(self) -> Dict[int, List[str]]:
        """
        Get the list of API functions parameters.
        """
        return {
            0: ["text"],
            1: ["commit_sha"],
            2: ["start_version", "end_version"],
        }

    def is_valid_submodule(self, submodule: str = ''):
        if not isinstance(submodule, str):
            raise TypeError("submodule only accepts string or empty string")
        if submodule in self.submodules or submodule == '':
            return True
        raise InvalidSubmoduleError()

    def get_commit_diff_files(self, commit_hash: str, submodule: str = '',):
        """
        Get the list of files changed in a commit.
        """
        # Validate input and task readiness
        self.is_valid_submodule(submodule=submodule)
        self.is_valid_commit(commit_hash=commit_hash, submodule=submodule)
        if not self.is_task_ready:
            raise RepositoryNotTaskReady()


        # Check if this is the initial commit by trying to get its parent
        try:
            self._git.execute(["rev-parse", f"{commit_hash}^"])
            has_parent = True
        except:
            has_parent = False

        if has_parent:
            diff_output = self._git.execute(["diff", "--name-only", commit_hash + "^", commit_hash])
        else:
            # For initial commit, compare with empty tree
            empty_tree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
            diff_output = self._git.execute(["diff", "--name-only", empty_tree, commit_hash])
        return diff_output.decode().splitlines()

    def is_valid_commit(self, commit_hash: str, submodule: str = ''):
        valid_commit = False
        if not commit_hash or not isinstance(commit_hash, str):
            raise TypeError("commit_hash only accepts string")
        if not isinstance(submodule, str):
            raise TypeError("submodule only accepts string or empty string")

        if submodule:
            valid_commit = self.submodule_has_commit(submodule_path=submodule, commit_sha=commit_hash)
        else:
            valid_commit = self.has_commit(commit_sha=commit_hash)
        if not valid_commit:
            raise InvalidCommitError()
        return valid_commit

    def get_file_content_at_commit(self, commit_hash: str, file_path: str, submodule: str = '',):
        """
        Get the content of a file at a specific commit.
        """

        try:
            # Validate input and task readiness
            self.is_valid_submodule(submodule=submodule)
            self.is_valid_commit(commit_hash=commit_hash, submodule=submodule)
            if not self.is_task_ready:
                raise RepositoryNotTaskReady()
            if not file_path:
                raise InvalidFilepathError()
            file_content = self._git.execute(["show", f"{commit_hash}:{file_path}"])
            return file_content
        except GitCommandError:
            # If the file does not exist in the commit (e.g., new file), return an empty string
            return ""

    def generate_commit_diff_html(self, commit_hash: str, submodule: str = '', output_html="commit_diff.html"):
        """
        Generate an HTML file showing diffs for all files changed in a specific commit.
        """
        try:
            # Validate input and task readiness
            self.is_valid_submodule(submodule=submodule)
            self.is_valid_commit(commit_hash=commit_hash, submodule=submodule)
            if not self.is_task_ready:
                raise RepositoryNotTaskReady()

            # Get changed files
            changed_files = self.get_commit_diff_files(commit_hash)

            html_content = []
            for file_path in changed_files:
                # Get file content before and after the commit
                old_content = self.get_file_content_at_commit(commit_hash + "^", file_path)
                new_content = self.get_file_content_at_commit(commit_hash, file_path)

                # Generate the HTML diff for the current file
                diff_html = difflib.HtmlDiff(wrapcolumn=80).make_file(
                    old_content.splitlines(),
                    new_content.splitlines(),
                    fromdesc=f"{file_path} (before)",
                    todesc=f"{file_path} (after)",
                    context=True,
                    numlines=3
                )
                html_content.append(diff_html)

            # Save the generated HTML
            html_body = "<br><br>".join(html_content)
            html_template = f"""
            <html>
            <head>
                <title>Commit Diff: {commit_hash}</title>
            </head>
            <body>
                <h1>Commit Diff: {commit_hash}</h1>
                {html_body}
            </body>
            </html>
            """
            output_path = Path(output_html)
            output_path.write_text(html_template, encoding="utf-8")
            return str(output_path)
        except TypeError as e:
            raise e
        except Exception as e:
            return f"Error: {str(e)}"