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
from version_finder import setup_logger
from version_finder import VersionFinder, GitError, VersionNotFoundError
from version_finder import VersionFinderTask, VersionFinderTaskRegistry
from version_finder import parse_arguments


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


class VersionFinderCLI:
    """
    Version Finder CLI class.
    """

    def __init__(self):
        """
        Initialize the VersionFinderCLI with a logger.
        """
        self.registry = VersionFinderTaskRegistry()
        self.logger = setup_logger()
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
            self.path = self.handle_path_input(args.path)
            self.finder = VersionFinder(path=self.path)

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

            task_validator = TaskNumberValidator(min_index, max_index)
            task_idx = int(prompt(
                "Enter task number: ",
                validator=task_validator,
                validate_while_typing=True
            ).strip())

            self.logger.debug("Selected task: %d", task_idx)
            if not self.registry.has_index(task_idx):
                self.logger.error("Invalid task selected")
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
        self.logger.info("Current branch: %s", current_branch)

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
            # Replace the existing input code with:
            commit_sha = prompt(
                "Enter commit SHA to search from (Ctrl+C to cancel): ",
                validator=CommitSHAValidator(),
                validate_while_typing=True
            ).strip()

            submodule_name = self.handle_submodule_input()

            self.logger.info("Searching for first version containing commit: %s", commit_sha)
            version = self.finder.find_first_version_containing_commit(commit_sha, submodule_name)

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
            first_version = prompt("Enter first version (Ctrl+C to cancel): ").strip()
            self.logger.info("First version: %s", first_version)
            second_version = prompt("Enter second version (Ctrl+C to cancel): ").strip()
            self.logger.info("Second version: %s", second_version)

            submodule_name = self.handle_submodule_input()
            self.logger.info("Searching for commits between versions: %s and %s", first_version, second_version)
            commits = self.finder.get_commits_between_versions(first_version, second_version, submodule_name)
            if not commits[0]:
                self.logger.info("No commits found between versions: %s and %s", first_version, second_version)
                return 0
            self.logger.info("\nFound %d commits:", len(commits))

            for i, commit in enumerate(commits, 1):
                self.logger.info("  %d. %s", i, commit)
        except KeyboardInterrupt:
            self.logger.info("\nSearch cancelled by user")
            return 1
        except VersionNotFoundError as e:
            self.logger.debug("Couldn't find input version. %s", str(e))
        except Exception as e:
            self.logger.error("Error during commit search: %s", str(e))
            return 1


def cli_main(args: argparse.Namespace) -> int:
    """Main entry point for the version finder CLI."""
    # Parse arguments
    if args.version:
        from .__version__ import __version__
        print(f"version_finder cli-v{__version__}")
        return 0

    # Setup logging
    logger = setup_logger(args.verbose)

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
