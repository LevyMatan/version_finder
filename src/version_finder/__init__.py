"""
main package for version_finder
"""

from typing import List

# version_finder/__init__.py
from .protocols import LoggerProtocol, NullLogger
from .core import VersionFinder, Commit, GitError, InvalidGitRepository, GitRepositoryNotClean, RepositoryNotTaskReady, InvalidCommitError, InvalidSubmoduleError, InvalidBranchError, GitNotInstalledError, VersionNotFoundError
from .git_executer import GitConfig, GitCommandError, GitCommandExecutor
from .logger.logger import setup_logger
__version__ = "7.0.0"

__all__: List[str] = [
    '__version__',

    # Git Executer
    'GitCommandExecutor',
    'GitConfig',
    'GitCommandError',

    # Core
    'VersionFinder',
    'Commit',
    'GitError',
    'InvalidGitRepository',
    'GitRepositoryNotClean',
    'RepositoryNotTaskReady',
    'InvalidCommitError',
    'InvalidSubmoduleError',
    'InvalidBranchError',
    'GitNotInstalledError',
    'VersionNotFoundError',

    # Logger
    'LoggerProtocol',
    'NullLogger',
    'setup_logger',
]
