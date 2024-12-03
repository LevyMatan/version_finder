"""
main package for version_finder
"""

from typing import List

# version_finder/__init__.py
from .protocols import LoggerProtocol, NullLogger
from .version_finder import VersionFinder, Commit, GitError, InvalidGitRepository, GitRepositoryNotClean, RepositoryNotTaskReady, InvalidCommitError, InvalidSubmoduleError, InvalidBranchError, GitNotInstalledError, VersionNotFoundError
from .version_finder import VersionFinderTask, VersionFinderTaskRegistry
from .git_executer import GitConfig, GitCommandError, GitCommandExecutor
from .logger import setup_logger
from .__common__ import parse_arguments, args_to_command
from .__version__ import __version__

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

    'VersionFinderTask',
    'VersionFinderTaskRegistry',

    # Logger
    'LoggerProtocol',
    'NullLogger',
    'setup_logger',

    # Common
    'parse_arguments',
    'args_to_command',
]
