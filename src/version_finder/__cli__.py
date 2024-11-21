# version_finder/__main__.py
import logging
import sys
from typing import List
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import argparse
from .core import VersionFinder, GitConfig, GitError
from .logger.logger import setup_logger
from .protocols import LoggerProtocol
from .__common__ import parse_arguments


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

        logger.info("\nSelect commit to view surrounding versions (Ctrl+C to cancel):")
        while True:
            try:
                selection = input("Enter commit number: ").strip()
                if not selection.isdigit():
                    logger.error("Invalid input. Please enter a number.")
                    continue

                index = int(selection) - 1
                if index < 0 or index >= len(commits):
                    logger.error("Invalid commit number selected")
                    continue

                selected_commit = commits[index]
                logger.info("Selected commit: %s", selected_commit)

                versions = finder.get_commit_surrounding_versions(selected_commit)
                logger.info("\nSurrounding versions:")
                logger.info("  Previous version: %s", finder.get_commit_version(versions[0]) or "None")
                logger.info("  Next version: %s", finder.get_commit_version(versions[1]) or "None")
                logger.info("  Previous version: %s", versions[0] or "None")
                logger.info("  Next version: %s", versions[1] or "None")

                break  # Exit loop if valid selection is made

            except KeyboardInterrupt:
                logger.info("\nOperation cancelled by user")
                return 0
            except Exception as e:
                logger.error("Error during version search: %s", str(e))
        return 0

    except KeyboardInterrupt:
        logger.info("\nSearch cancelled by user")
        return 1
    except Exception as e:
        logger.error("Error during commit search: %s", str(e))
        return 1


def cli_main(args: argparse.Namespace) -> int:
    """Main entry point for the version finder CLI."""
    # Parse arguments

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(__name__, level=log_level)

    logger.debug("Starting Version Finder")
    logger.debug("Arguments: %s", args)

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
        logger.error("Git error: %s", str(e))
        return 1


def main() -> int:

    args = parse_arguments()
    return cli_main(args)


if __name__ == "__main__":
    sys.exit(main())
