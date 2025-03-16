"""
common.py
====================================
Common utilities and constants for version_finder.
"""
import argparse
import os
from pathlib import Path
from typing import Optional

# Default configuration values
DEFAULT_GIT_TIMEOUT = 30  # seconds
DEFAULT_GIT_MAX_RETRIES = 0
DEFAULT_GIT_RETRY_DELAY = 1  # seconds

# Environment variable names
ENV_GIT_TIMEOUT = "GIT_TIMEOUT"
ENV_GIT_MAX_RETRIES = "GIT_MAX_RETRIES"
ENV_GIT_RETRY_DELAY = "GIT_RETRY_DELAY"
ENV_DEBUG = "VERSION_FINDER_DEBUG"

# Git command constants
GIT_CMD_FETCH = ["fetch", "--all"]
GIT_CMD_CHECKOUT = ["checkout"]
GIT_CMD_SUBMODULE_UPDATE = ["submodule", "update", "--init", "--recursive"]
GIT_CMD_LIST_BRANCHES = ["branch", "-a"]
GIT_CMD_LIST_SUBMODULES = ["submodule", "status"]
GIT_CMD_LOG = ["log"]
GIT_CMD_SHOW = ["show"]
GIT_CMD_REV_PARSE = ["rev-parse"]
GIT_CMD_GREP = ["grep"]

# Regex patterns
BRANCH_PATTERN = r"\s*(?:\*\s)?(.*)"

# UI constants
MAX_COMMITS_DISPLAY = 1000  # Maximum number of commits to display in UI
MAX_LOG_ENTRIES = 500  # Maximum number of log entries to keep in UI

# File paths
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.version_finder/config.json")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Version Finder - Find and compare versions in Git repositories")
    parser.add_argument("--path", "-p", type=str, default="", help="Path to the Git repository")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH, help="Path to configuration file")
    parser.add_argument("--version", "-v", action="store_true", help="Show version information")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force operation even if repository has uncommitted changes")
    parser.add_argument("--restore-state", "-r", action="store_true",
                        help="Restore repository to original state after operation")
    parser.add_argument("--branch", "-b", type=str, help="Branch to use")
    parser.add_argument("--commit", type=str, help="Commit SHA to find version for")
    parser.add_argument("--submodule", "-s", type=str, help="Submodule to use")
    parser.add_argument("--cli", action="store_true", help="Run the CLI version")
    parser.add_argument("--gui", action="store_true", help="Run the GUI version")
    parser.add_argument("--task", "-t", type=str, help="Task to run")

    return parser.parse_args()


def get_repository_path(path_arg: str) -> Optional[Path]:
    """
    Get the repository path from the command-line argument or current directory.

    Args:
        path_arg: Path argument from command line

    Returns:
        Path: Repository path or None if invalid
    """
    if path_arg:
        path = Path(path_arg)
    else:
        path = Path.cwd()

    # Check if path exists and is a directory
    if not path.exists() or not path.is_dir():
        return None

    # Check if it's a git repository
    git_dir = path / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return None

    return path


def args_to_command(args):
    """
    Convert argparse.Namespace object to command-line arguments string.

    Args:
        args: argparse.Namespace object containing command-line arguments

    Returns:
        str: Command-line arguments as a string

    Raises:
        AttributeError: If args is not an argparse.Namespace object
    """
    if not isinstance(args, argparse.Namespace):
        raise AttributeError("args must be an argparse.Namespace object")

    command_parts = []

    for key, value in vars(args).items():
        # Replace underscores with hyphens in argument names
        arg_name = key.replace('_', '-')

        # Include boolean flags that are True
        if isinstance(value, bool):
            if value:
                command_parts.append(f"--{arg_name}")
        # Include non-None and non-False values
        elif value is not None:
            command_parts.append(f"--{arg_name} {value}")

    return " ".join(command_parts)
