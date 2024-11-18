# version_finder/__main__.py
import argparse
import logging
import subprocess
import sys
import shutil
from typing import List
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from .core import VersionFinder, GitConfig, GitError
from .logger.logger import setup_logger
from .protocols import LoggerProtocol
from ._version import __version__


def verify_git_dependency(logger: LoggerProtocol) -> None:
    """
    Verify that git is installed and accessible.
    """
    git_path = shutil.which('git')

    if git_path is None:
        logger.error("""
Git is not found in your system PATH. Please ensure that:
1. Git is installed on your system
2. Git is added to your system PATH

You can download Git from: https://git-scm.com/downloads

After installing:
1. Close and reopen your terminal
2. Verify installation with: git --version
""")
        sys.exit(1)

    try:
        subprocess.run([git_path, "--version"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

    except subprocess.CalledProcessError as e:
        logger.error(f"""
Git was found at {git_path} but failed to execute.
Error: {e.stderr.decode('utf-8', errors='replace')}
""")
        sys.exit(1)
    except Exception as e:
        logger.error(f"""
An unexpected error occurred while running git:
{str(e)}
""")
        sys.exit(1)

    logger.debug(f"Git found at: {git_path}")


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Version Finder - A tool to find and compare versions in Git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -p /path/to/repo                 # Find versions in specified repository
  %(prog)s -v                               # Run with verbose output
  %(prog)s --timeout 60                     # Set git operation timeout to 60 seconds
  %(prog)s --retries 3                      # Set number of retries for git operations
""")

    parser.add_argument("-p", "--path",
                        help="Repository path (defaults to current directory)")

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enable verbose output")

    parser.add_argument("--timeout",
                        type=int,
                        default=30,
                        help="Git operation timeout in seconds (default: 30)")

    parser.add_argument("--retries",
                        type=int,
                        default=0,
                        help="Number of retries for git operations (default: 0)")

    parser.add_argument('--version',
                        action='version',
                        version=f'%(prog)s {__version__}',
                        help="Show program's version number and exit")

    args = parser.parse_args()

    # Validate timeout
    if args.timeout <= 0:
        parser.error("Timeout must be greater than 0")

    # Validate retries
    if args.retries < 0:
        parser.error("Number of retries cannot be negative")

    return args


def get_branch_selection(branches: List[str], logger: LoggerProtocol) -> str:
    """
    Get branch selection from user with auto-completion.

    Args:
        branches: List of available branches
        logger: Logger instance

    Returns:
        Selected branch name
    """
    branch_completer = WordCompleter(branches, ignore_case=True)

    while True:
        try:
            logger.debug("\nAvailable branches:")
            for branch in branches:
                logger.debug(f"  - {branch}")

            branch = prompt(
                "\nEnter branch name (Tab for completion): ",
                completer=branch_completer,
                complete_while_typing=True
            ).strip()

            if branch in branches:
                return branch

            logger.error("Invalid branch selected")

        except (KeyboardInterrupt, EOFError):
            logger.info("\nOperation cancelled by user")
            sys.exit(0)


def process_commit_search(finder: VersionFinder, branch: str, logger: LoggerProtocol):
    """
    Process commit search by getting user input and displaying results.

    Args:
        finder: VersionFinder instance
        branch: Name of the branch to search
        logger: Logger instance

    Returns:
        int: 0 on success, 1 on error
    """
    try:
        logger.info("Enter text to search for in commits (Ctrl+C to cancel):")
        text = input().strip()

        if not text:
            logger.warning("Search text cannot be empty")
            return 1

        logger.info("Searching for commits containing: %s", text)
        commits = finder.find_commits_by_text(branch, text)

        if not commits:
            logger.info("No commits found containing: %s", text)
            return 0

        max_commits = 50  # Define reasonable limit
        if len(commits) > max_commits:
            logger.warning(
                "Found %d commits. Please refine your search text (max: %d)",
                len(commits), max_commits
            )
            return 1

        logger.info("\nFound %d commits:", len(commits))
        for i, commit in enumerate(commits, 1):
            logger.info("  %d. %s", i, commit)

        return 0

    except KeyboardInterrupt:
        logger.info("\nSearch cancelled by user")
        return 1
    except Exception as e:
        logger.error("Error during commit search: %s", str(e))
        return 1


def main() -> int:
    """Main entry point for the version finder CLI."""
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(__name__, level=log_level)

    logger.debug("Starting Version Finder")
    logger.debug("Arguments: %s", args)

    # Verify git installation
    verify_git_dependency(logger)

    try:
        # Create git configuration
        config = GitConfig(
            timeout=args.timeout,
            max_retries=args.retries
        )

        # Initialize VersionFinder
        logger.debug("Initializing VersionFinder with path: %s ", args.path)

        finder = VersionFinder(
            path=args.path,
            config=config,
            logger=logger
        )

        # Get available branches
        logger.debug("Fetching available branches")
        branches = finder.get_branches()
        if not branches:
            logger.error("No branches found in repository")
            return 1

        # Get branch selections for comparison
        logger.info("\nSelect branch:")
        branch = get_branch_selection(branches, logger)
        logger.info("Selected branch: %s", branch)

        # Look for a commit in the branch
        finder.update_repository(branch)
        logger.info("Repository updated to branch: %s", branch)
        process_commit_search(finder, branch, logger)

    except GitError as e:
        logger.error(f"Git error: {str(e)}")
        return 1
    #     logger.info("\nOperation cancelled by user")
    #     return 0
    # except Exception as e:
    #     logger.error(f"Unexpected error: {str(e)}")
    #     if args.verbose:
    #         logger.debug(traceback.format_exc())
    #     return 1


if __name__ == "__main__":
    sys.exit(main())
