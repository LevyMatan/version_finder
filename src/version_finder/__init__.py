"""
main package for version_finder
"""

from typing import List

# version_finder/__init__.py
from .protocols import LoggerProtocol, NullLogger
from .core import VersionFinder, GitError, InvalidGitRepository, GitRepositoryNotClean, RepositoryNotTaskReady, InvalidCommitError, InvalidSubmoduleError, InvalidBranchError, GitNotInstalledError
from .git_executer import GitConfig, GitCommandError, GitCommandExecutor
from .logger.logger import setup_logger
__version__ = "5.4.1"

__all__: List[str] = [
    '__version__',

    # Git Executer
    'GitCommandExecutor',
    'GitConfig',
    'GitCommandError',

    # Core
    'VersionFinder',
    'GitError',
    'InvalidGitRepository',
    'GitRepositoryNotClean',
    'RepositoryNotTaskReady',
    'InvalidCommitError',
    'InvalidSubmoduleError',
    'InvalidBranchError',
    'GitNotInstalledError',

    # Logger
    'LoggerProtocol',
    'NullLogger',
    'setup_logger',
]
