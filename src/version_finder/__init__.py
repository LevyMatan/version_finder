"""
main package for version_finder
"""

from typing import List

# version_finder/__init__.py
from .core import VersionFinder, GitConfig, GitError
from .logger.logger import setup_logger
__version__ = "5.2.1"

__all__: List[str] = [
    'VersionFinder',
    'GitConfig',
    'GitError',
    'setup_logger',
    '__version__'
]
