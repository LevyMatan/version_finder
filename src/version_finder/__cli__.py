# version_finder/__main__.py
import logging
import sys
import os
from typing import List, Any
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import argparse
from version_finder.core import VersionFinder, GitError, VersionFinderTask, VersionFinderTaskRegistry
from version_finder.logger.logger import setup_logger
from version_finder.protocols import LoggerProtocol
from version_finder.__common__ import parse_arguments

__cli_version__ = "1.0.0"


class VersionFinderCLI:
    """
    Version Finder CLI class.
    """

    def __init__(self, logger: LoggerProtocol):
        """
        Initialize the VersionFinderCLI with a logger.

        Args:
            logger: Logger instance for logging operations.
        """
        self.registry = VersionFinderTaskRegistry()
        self.logger = logger
        self.logger.info("Version Finder CLI v%s", __cli_version__)

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
                tasks_actions[task.index] = (self.find_commit_by_text)
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
            self.path = VersionFinderCLI.handle_path_input(args.path)
            self.finder = VersionFinder(path=self.path, logger=self.logger)

            actions = self.get_task_functions()
            params = self.finder.get_task_api_functions_params()
            self.registry.initialize_actions_and_args(actions, params)

            self.branch = self.handle_branch_input(args.branch)

            self.finder.update_repository(self.branch)

            self.task_name = self.handle_task_input(args.task)

            self.run_task(self.task_name)

        except KeyboardInterrupt:
            self.logger.info("\nOperation cancelled by user")
            return 0
        except Exception as e:
            self.logger.error("Error during task execution: %s", str(e))
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
            print(f"Choose from tasks {min_index} to {max_index}")
            # Clean the input more thoroughly
            try:
                # Use raw_input if available (Python 2) or input (Python 3)
                user_input = input().replace('\r', '').replace('\n', '').strip()
                task_idx = int(user_input)
            except ValueError:
                self.logger.error("Invalid input: please enter a number")
                sys.exit(1)

        self.logger.debug("Selected task: %d", task_idx)
        if not self.registry.has_index(task_idx):
            self.logger.error("Invalid task selected")
            sys.exit(1)

        task_struct = self.registry.get_by_index(task_idx)
        return task_struct.name

    def handle_branch_input(self, branch_name: str) -> str:
        """
        Handle branch input from user.
        """
        if branch_name is None:
            print("You have not selected a branch.")
            current_branch = self.finder.get_current_branch()
            self.logger.info("Current branch: %s", current_branch)
            if current_branch:
                print(f"Would you like to use the current checked-out branch: {current_branch} (y/n)")
                use_current = input().strip().lower()
                if use_current == "y":
                    return current_branch

            branch_name = self.get_branch_selection()

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

    def handle_path_input(path: str) -> str:
        """
        Handle path input from user.

        Args:
            logger: Logger instance

        Returns:
            str: Path entered by user
        """
        if path is None:
            print("Repository path was not provided.")
            print(f"Press [ENTER] to use the current directory: {os.getcwd()}")
            print("Or enter a repository path:")

            # Take input from user
            path = input().strip()
            if not path:
                path = os.getcwd()

        return path

    def get_branch_selection(self) -> str:
        """
        Get branch selection from user with auto-completion.

        Args:
            branches: List of available branches
            logger: Logger instance

        Returns:
            Selected branch name
        """
        branches = self.finder.list_branches()
        branch_completer = WordCompleter(branches, ignore_case=True, match_middle=True)

        while True:
            try:
                self.logger.debug("\nAvailable branches:")
                for branch in branches:
                    self.logger.debug(f"  - {branch}")

                branch = prompt(
                    "\nEnter branch name (Tab for completion): ",
                    completer=branch_completer,
                    complete_while_typing=True
                ).strip()

                if branch in branches:
                    return branch

                self.logger.error("Invalid branch selected")

            except (KeyboardInterrupt, EOFError):
                self.logger.info("\nOperation cancelled by user")
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

    def find_commit_by_text(self):
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
            text = prompt("Enter search text: ").strip()


            if not text:
                self.logger.warning("Search text cannot be empty")
                return 1

            submodule_name = self.handle_submodule_input()

            self.logger.info("Searching for commits containing: %s", text)
            commits = self.finder.find_commits_by_text(text, submodule_name)

            if not commits:
                self.logger.info("No commits found containing: %s", text)
                return 0

            max_commits = 50  # Define reasonable limit
            if len(commits) > max_commits:
                self.logger.warning(
                    "Found %d commits. Please refine your search text (max: %d)",
                    len(commits), max_commits
                )
                return 1

            self.logger.info("\nFound %d commits:", len(commits))
            for i, commit in enumerate(commits, 1):
                self.logger.info("  %d. %s", i, commit)

        except KeyboardInterrupt:
            self.logger.info("\nSearch cancelled by user")
            return 1
        except Exception as e:
            self.logger.error("Error during commit search: %s", str(e))
            return 1

    def find_first_version_containing_commit(self):
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
            self.logger.info("Enter commit SHA to search from (Ctrl+C to cancel):")
            commit_sha = input().strip()

            if not commit_sha:
                self.logger.warning("Commit SHA cannot be empty")
                return 1

            self.logger.info("Searching for first version containing commit: %s", commit_sha)
            version = self.finder.find_first_version_containing_commit(self.branch, commit_sha)

            if not version:
                self.logger.info("No version found containing commit: %s", commit_sha)
                return 0

            self.logger.info("\nFound version: %s", version)

        except KeyboardInterrupt:
            self.logger.info("\nSearch cancelled by user")
            return 1
        except Exception as e:
            self.logger.error("Error during version search: %s", str(e))
            return 1

    def find_all_commits_between_versions(self):
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
            self.logger.info("Enter first version (Ctrl+C to cancel):")
            first_version = input().strip()
            self.logger.info("Enter second version (Ctrl+C to cancel):")
            second_version = input().strip()
            self.logger.info("Searching for commits between versions: %s and %s", first_version, second_version)
            commits = self.finder.find_commits_between_versions(first_version, second_version)
            if not commits:
                self.logger.info("No commits found between versions: %s and %s", first_version, second_version)
                return 0
            self.logger.info("\nFound %d commits:", len(commits))

            for i, commit in enumerate(commits, 1):
                self.logger.info("  %d. %s", i, commit)
        except KeyboardInterrupt:
            self.logger.info("\nSearch cancelled by user")
            return 1
        except Exception as e:
            self.logger.error("Error during commit search: %s", str(e))
            return 1


def cli_main(args: argparse.Namespace) -> int:
    """Main entry point for the version finder CLI."""
    # Parse arguments

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(__name__, level=log_level)

    # Initialize CLI
    cli = VersionFinderCLI(logger)
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
