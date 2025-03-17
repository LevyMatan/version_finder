# version_finder/__main__.py
import argparse
import sys
import os
import re
from typing import List, Any
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter, PathCompleter
from prompt_toolkit.validation import Validator, ValidationError
from version_finder.logger import get_logger
from version_finder.version_finder import VersionFinder, GitError
from version_finder.version_finder import VersionFinderTask, VersionFinderTaskRegistry
from version_finder.common import parse_arguments
import threading
import time

# Initialize module logger
logger = get_logger(__name__)


class TaskNumberValidator(Validator):
    def __init__(self, min_index: int, max_index: int):
        self.min_index = min_index
        self.max_index = max_index

    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(message="Task number cannot be empty")
        try:
            task_idx = int(text)
            if not (self.min_index <= task_idx <= self.max_index):
                raise ValidationError(
                    message=f"Please select a task number between {self.min_index} and {self.max_index}")
        except ValueError:
            raise ValidationError(message="Please enter a valid number")


class CommitSHAValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(message="Commit SHA cannot be empty")
        # Allow full SHA (40 chars), short SHA (min 7 chars), or HEAD~n format
        if not (len(text) >= 7 and len(text) <= 40) and not text.startswith("HEAD~"):
            raise ValidationError(message="Invalid commit SHA format. Use 7-40 hex chars or HEAD~n format")


class ProgressIndicator:
    """A simple progress indicator for CLI operations"""

    def __init__(self, message="Processing"):
        self.message = message
        self.running = False
        self.thread = None

    def start(self):
        """Start the progress indicator"""
        self.running = True
        self.thread = threading.Thread(target=self._show_progress)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the progress indicator"""
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the indicator line
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def _show_progress(self):
        """Show the progress indicator animation"""
        symbols = ["-", "\\", "|", "/"]
        i = 0
        while self.running:
            sys.stdout.write(f"\r{self.message} {symbols[i]} ")
            sys.stdout.flush()
            time.sleep(0.1)
            i = (i + 1) % len(symbols)


def with_progress(message):
    """Decorator to add progress indicator to functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            progress = ProgressIndicator(message)
            progress.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                progress.stop()
        return wrapper
    return decorator


class VersionFinderCLI:
    """
    Version Finder CLI class.
    """

    def __init__(self):
        """
        Initialize the VersionFinderCLI with a logger.
        """
        self.registry = VersionFinderTaskRegistry()
        self.prompt_style = Style.from_dict({
            # User input (default text).
            # '':          '#ff0066',

            # Prompt.
            'current_status': '#00aa00',
        })

    def get_task_functions(self) -> List[VersionFinderTask]:
        """
        Get the list of available task functions.

        Returns:
            List[VersionFinderTask]: List of available task functions.
        """
        tasks_actions = {}
        for task in self.registry._tasks_by_index.values():
            if (task.name == "Find all commits between two versions"):
                tasks_actions[task.index] = (self.find_all_commits_between_versions)
                continue
            if (task.name == "Find commit by text"):
                tasks_actions[task.index] = (self.find_commits_by_text)
                continue
            if (task.name == "Find first version containing commit"):
                tasks_actions[task.index] = (self.find_first_version_containing_commit)
                continue
        return tasks_actions

    def run(self, args: argparse.Namespace):
        """
        Run the CLI with the provided arguments.

        Args:
            args: Parsed command-line arguments.

        Returns:
            int: 0 on success, 1 on error
        """
        try:
            self.path = self.handle_path_input(args.path)

            # Initialize VersionFinder with force=True to allow uncommitted changes
            self.finder = VersionFinder(path=self.path, force=True)

            # Check for uncommitted changes
            state = self.finder.get_saved_state()
            if state.get("has_changes", False):
                logger.warning("Repository has uncommitted changes")
                has_submodules = bool(state.get("submodules", {}))

                if not args.force:
                    # Build message with details about what will happen
                    message = (
                        "Repository has uncommitted changes. Version Finder will:\n"
                        "1. Stash your changes with a unique identifier\n"
                        "2. Perform the requested operations\n"
                        "3. Restore your original branch and stashed changes when closing\n"
                    )

                    if has_submodules:
                        message += "Submodules with uncommitted changes will also be handled similarly.\n"

                    message += "Proceed anyway? (y/N): "

                    proceed = input(message).lower() == 'y'
                    if not proceed:
                        logger.info("Operation cancelled by user")
                        return 0

            actions = self.get_task_functions()
            params = self.finder.get_task_api_functions_params()
            self.registry.initialize_actions_and_args(actions, params)

            self.branch = self.handle_branch_input(args.branch)

            self.finder.update_repository(self.branch)

            self.task_name = self.handle_task_input(args.task)

            self.run_task(self.task_name)

            # Restore original state if requested
            if args.restore_state:
                logger.info("Restoring original repository state")

                # Get the state before restoration for logging
                state = self.finder.get_saved_state()
                has_changes = state.get("has_changes", False)
                stash_created = state.get("stash_created", False)

                if has_changes:
                    if stash_created:
                        logger.info("Attempting to restore stashed changes")
                    else:
                        logger.warning("Repository had changes but they were not stashed")

                # Perform the restoration
                if self.finder.restore_repository_state():
                    logger.info("Original repository state restored successfully")

                    # Verify the restoration
                    current_branch = self.finder.get_current_branch()
                    original_branch = state.get("branch")
                    if original_branch and current_branch:
                        if original_branch.startswith("HEAD:"):
                            logger.info("Restored to detached HEAD state")
                        else:
                            logger.info(f"Restored to branch: {current_branch}")

                    # Check if we still have uncommitted changes
                    if has_changes and self.finder.has_uncommitted_changes():
                        logger.info("Uncommitted changes were successfully restored")
                    elif has_changes and not self.finder.has_uncommitted_changes():
                        logger.error("Failed to restore uncommitted changes")
                else:
                    logger.warning("Failed to restore original repository state")

        except KeyboardInterrupt:
            logger.info("\nOperation cancelled by user")

            # Try to restore original state
            if hasattr(self, 'finder') and self.finder and args.restore_state:
                logger.info("Restoring original repository state")
                if self.finder.restore_repository_state():
                    logger.info("Original repository state restored successfully")
                else:
                    logger.warning("Failed to restore original repository state")

            return 0
        except Exception as e:
            logger.error("Error during task execution: %s", str(e))

            # Try to restore original state
            if hasattr(self, 'finder') and self.finder and args.restore_state:
                logger.info("Restoring original repository state")
                if self.finder.restore_repository_state():
                    logger.info("Original repository state restored successfully")
                else:
                    logger.warning("Failed to restore original repository state")

            return 1

    def handle_task_input(self, task_name: str) -> str:
        """
        Handle task input from user.
        """
        if task_name is None:
            print("You have not selected a task.")
            print("Please select a task:")
            # Iterate through tasks in index order
            for task in self.registry.get_tasks_by_index():
                print(f"{task.index}: {task.name}")
            min_index = self.registry.get_tasks_by_index()[0].index
            max_index = self.registry.get_tasks_by_index()[-1].index

            task_validator = TaskNumberValidator(min_index, max_index)
            task_idx = int(prompt(
                "Enter task number: ",
                validator=task_validator,
                validate_while_typing=True
            ).strip())

            logger.debug("Selected task: %d", task_idx)
            if not self.registry.has_index(task_idx):
                logger.error("Invalid task selected")
                sys.exit(1)

            task_struct = self.registry.get_by_index(task_idx)
            return task_struct.name

    def handle_branch_input(self, branch_name: str) -> str:
        """
        Handle branch input from user with auto-completion.

        Args:
            branch_name: Optional branch name from command line

        Returns:
            str: Selected branch name
        """
        if branch_name is not None:
            return branch_name

        branches = self.finder.list_branches()
        # When creating the branch_completer, modify it to:
        branch_completer = WordCompleter(
            branches,
            ignore_case=True,
            match_middle=True,
            pattern=re.compile(r'\S+')  # Matches non-whitespace characters
        )

        current_branch = self.finder.get_current_branch()
        logger.info("Current branch: %s", current_branch)

        if current_branch:
            prompt_message = [
                ('', 'Current branch: '),
                ('class:current_status', f'{current_branch}'),
                ('', '\nPress [ENTER] to use the current branch or type to select a different branch: '),
            ]
            branch_name = prompt(
                prompt_message,
                completer=branch_completer,
                complete_while_typing=True,
                style=self.prompt_style
            ).strip()
            if branch_name == "":
                return current_branch
            return branch_name

    def handle_submodule_input(self, submodule_name: str = None) -> str:
        """
        Handle branch input from user.
        """
        if submodule_name is None:
            submodule_list = self.finder.list_submodules()
            submodule_completer = WordCompleter(submodule_list, ignore_case=True, match_middle=True)
            # Take input from user
            submodule_name = prompt(
                "\nEnter submodule name (Tab for completion) or [ENTER] to continue without a submodule:",
                completer=submodule_completer,
                complete_while_typing=True
            ).strip()
        return submodule_name

    def handle_path_input(self, path: str = None) -> str:
        """
        Handle path input from user using prompt_toolkit.

        Args:
            path: Optional path from command line

        Returns:
            str: Path entered by user
        """
        if path is None:
            prompt_msg = [
                ('', 'Current directory: '),
                ('class:current_status', f'{os.getcwd()}'),
                ('', ':\nPress [ENTER] to use the current directory or type to select a different directory: '),
            ]

            path_completer = PathCompleter(
                only_directories=True,
                expanduser=True
            )
            path = prompt(
                prompt_msg,
                completer=path_completer,
                complete_while_typing=True,
                style=self.prompt_style
            ).strip()

            if not path:
                path = os.getcwd()

        # Validate the path
        if not os.path.exists(path) or not os.path.isdir(path):
            print(f"Error: Invalid path '{path}'", file=sys.stderr)
            sys.exit(1)

        return path

    def get_branch_selection(self) -> str:
        """
        Get branch selection from user with auto-completion.

        Returns:
            Selected branch name
        """
        branches = self.finder.list_branches()
        branch_completer = WordCompleter(branches, ignore_case=True, match_middle=True)

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

    def run_task(self, task_name: str):
        """
        Run the selected task.
        """
        # task_args = self.fetch_arguments_per_task(task_name)
        self.registry.get_by_name(task_name).run()

    def fetch_arguments_per_task(self, task_name: str) -> List[Any]:
        """
        Fetch arguments for the selected task.
        """
        task_args = []
        for arg_name in self.registry.get_by_name(task_name).args:
            arg_value = getattr(self, arg_name)
            task_args.append(arg_value)
        return task_args

    @with_progress("Finding version for commit")
    def find_first_version_containing_commit(self, commit_sha: str, submodule: str = None):
        """
        Find the first version containing a commit.

        Args:
            commit_sha: The commit SHA to find the version for
            submodule: Optional submodule path
        """
        try:
            version = self.finder.find_version(commit_sha, submodule)
            if version:
                print(f"\nVersion for commit {commit_sha}: {version}")
            else:
                print(f"\nNo version found for commit {commit_sha}")
        except Exception as e:
            print(f"\nError: {str(e)}")

    @with_progress("Finding commits between versions")
    def find_all_commits_between_versions(self, from_version: str, to_version: str, submodule: str = None):
        """
        Find all commits between two versions.

        Args:
            from_version: The starting version
            to_version: The ending version
            submodule: Optional submodule path
        """
        try:
            commits = self.finder.get_commits_between_versions(from_version, to_version, submodule)
            if commits:
                print(f"\nFound {len(commits)} commits between {from_version} and {to_version}:")
                for commit in commits:
                    print(f"{commit.sha[:8]} - {commit.subject}")
            else:
                print(f"\nNo commits found between {from_version} and {to_version}")
        except Exception as e:
            print(f"\nError: {str(e)}")

    @with_progress("Searching for commits")
    def find_commits_by_text(self, text: str, submodule: str = None):
        """
        Find commits containing specific text.

        Args:
            text: The text to search for
            submodule: Optional submodule path
        """
        try:
            commits = self.finder.find_commits_by_text(text, submodule)
            if commits:
                print(f"\nFound {len(commits)} commits containing '{text}':")
                for commit in commits:
                    print(f"{commit.sha[:8]} - {commit.subject}")
            else:
                print(f"\nNo commits found containing '{text}'")
        except Exception as e:
            print(f"\nError: {str(e)}")


def cli_main(args: argparse.Namespace) -> int:
    """Main entry point for the version finder CLI."""
    # Parse arguments
    if args.version:
        from .__version__ import __version__
        print(f"version_finder cli-v{__version__}")
        return 0

    # Initialize CLI
    cli = VersionFinderCLI()
    # Run CLI
    try:
        cli.run(args)
        return 0
    except GitError as e:
        logger.error("Git operation failed: %s", e)
        return 1


def main() -> int:

    args = parse_arguments()
    return cli_main(args)


if __name__ == "__main__":
    sys.exit(main())
