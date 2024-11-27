import pytest
import os
import tempfile
from pathlib import Path
import logging
from src.version_finder.core import (
    VersionFinder,
    GitConfig,
    InvalidGitRepository,
    GitRepositoryNotClean,
    GitCommandError
)
from src.version_finder.logger.logger import setup_logger

debug_logger = setup_logger(__name__, level=logging.DEBUG)


class TestGitConfig:
    def test_init_with_defaults(self):
        config = GitConfig()
        assert config.timeout == 30
        assert config.max_retries == 0
        assert config.retry_delay == 1

    def test_init_with_custom_values(self):
        config = GitConfig(timeout=20, max_retries=5, retry_delay=2)
        assert config.timeout == 20
        assert config.max_retries == 5
        assert config.retry_delay == 2

    def test_init_with_invalid_timeout(self):
        with pytest.raises(ValueError):
            GitConfig(timeout=-1)

    def test_init_with_invalid_max_retries(self):
        with pytest.raises(ValueError):
            GitConfig(max_retries=-1)


class TestVersionFinder:
    @pytest.fixture
    def test_repo(self):
        """Creates a temporary test repository with initial commit"""
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)

        # Initialize repo and create initial commit
        os.system("git init")
        os.system("git config user.email 'test@example.com'")
        os.system("git config user.name 'Test User'")
        os.system("touch file1")
        os.system("git add file1")
        os.system("git commit -m 'Initial commit'")

        # Create test branches
        os.system("git branch dev")
        os.system("git branch feature")

        yield temp_dir

        # Cleanup
        os.system(f"rm -rf {temp_dir}")

    def test_init_valid_repository(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        assert finder.repository_path == Path(test_repo).resolve()
        assert isinstance(finder.config, GitConfig)

    def test_init_invalid_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(InvalidGitRepository):
                VersionFinder(path=temp_dir)

    def test_list_branches(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        branches = finder.list_branches()
        assert 'main' in branches or 'master' in branches
        assert 'dev' in branches
        assert 'feature' in branches

    def test_has_branch(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        assert finder.has_branch('dev')
        assert not finder.has_branch('nonexistent-branch')

    def test_update_repository_valid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        finder.update_repository('dev')
        # Verify we're on dev branch
        result = os.popen('git branch --show-current').read().strip()
        assert result == 'dev'

    def test_update_repository_invalid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        with pytest.raises(GitCommandError):
            finder.update_repository('nonexistent-branch')

    def test_get_current_branch(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)

        # Test getting current branch on main
        current_branch = finder.get_current_branch()
        assert current_branch in ['main']

        # Test getting current branch after switching to dev
        finder.update_repository('dev')
        current_branch = finder.get_current_branch()
        assert current_branch == 'dev'

        # Test getting current branch after switching to feature
        finder.update_repository('feature')
        current_branch = finder.get_current_branch()
        assert current_branch == 'feature'

        # Get current commit hash
        commit_hash = os.popen('git rev-parse HEAD').read().strip()
        # Checkout specific commit to enter detached HEAD state
        os.system(f"git checkout {commit_hash}")
        current_branch = finder.get_current_branch()
        assert current_branch is None

    def test_extract_version_from_message(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)

        # Test various version formats
        test_cases = [
            ("Version: 2024_01", "2024_01"),
            ("Version: XX_2024_01_15", "2024_01_15"),
            ("Random text Version: 2024-01-15 more text", "2024-01-15"),
            ("2024_01_15_23", "2024_01_15_23"),
            ("Version: XX_2024_01", "2024_01"),
            ("No version here", None),
            ("2023-text", None),
            ("Version: XX_2024_01_15_RC1", "2024_01_15"),
            ("Version: 2024_01-15", "2024_01-15"),
        ]

        for message, expected in test_cases:
            result = finder._VersionFinder__extract_version_from_message(message)
            assert result == expected, f"Failed for message: {message}"

    def test_find_first_version_containing_commit_basic(self, test_repo):
        # Setup test repository with version commits
        os.chdir(test_repo)
        os.system("git checkout main")
        os.system("git commit -m 'Initial commit' --allow-empty")
        commit_to_find = os.popen('git rev-parse HEAD').read().strip()
        os.system("git commit -m 'Version: 2024_01' --allow-empty")

        finder = VersionFinder(path=test_repo)
        finder.update_repository('main')
        version = finder.find_first_version_containing_commit(commit_to_find)
        assert version == '2024_01'

    def test_find_first_version_containing_commit_multiple_versions(self, test_repo):
        os.chdir(test_repo)
        os.system("git checkout main")
        os.system("git commit -m 'Version: 2024_01' --allow-empty")
        os.system("git commit -m 'Some commit' --allow-empty")
        commit_to_find = os.popen('git rev-parse HEAD').read().strip()
        os.system("git commit -m 'Version: 2024_02' --allow-empty")
        os.system("git commit -m 'Version: 2024_03' --allow-empty")

        finder = VersionFinder(path=test_repo)
        finder.update_repository('main')
        version = finder.find_first_version_containing_commit(commit_to_find)
        assert version == '2024_02'

    def test_find_first_version_containing_commit_with_submodule(self, repo_with_submodule):
        # Setup submodule with specific commit
        os.chdir(os.path.join(repo_with_submodule, 'sub_repo'))
        os.system("git commit -m 'Submodule commit' --allow-empty")
        submodule_commit = os.popen('git rev-parse HEAD').read().strip()

        # Update main repo with version
        os.chdir(repo_with_submodule)
        os.system("git add sub_repo")
        os.system("git commit -m 'Version: 2024_01' --allow-empty")

        finder = VersionFinder(path=repo_with_submodule)
        finder.update_repository('main')
        version = finder.find_first_version_containing_commit(submodule_commit, submodule='sub_repo')
        assert version == '2024_01'

    def test_find_first_version_containing_commit_nonexistent_commit(self, test_repo):
        finder = VersionFinder(path=test_repo)
        with pytest.raises(GitCommandError):
            finder.update_repository('main')
            finder.find_first_version_containing_commit('nonexistent-commit')

    def test_find_first_version_containing_commit_no_version_after(self, test_repo):
        os.chdir(test_repo)
        os.system("git checkout main")
        os.system("git commit -m 'Version: 2024_01' --allow-empty")
        os.system("git commit -m 'Latest commit' --allow-empty")
        commit_to_find = os.popen('git rev-parse HEAD').read().strip()

        finder = VersionFinder(path=test_repo)
        finder.update_repository('main')
        version = finder.find_first_version_containing_commit(commit_to_find)
        assert version is None

    def test_get_commit_surrounding_versions(self, test_repo):
        os.chdir(test_repo)
        os.system("git checkout main")
        os.system("git commit -m 'Version: 2024_01' --allow-empty")
        os.system("git commit -m 'Middle commit' --allow-empty")
        middle_commit = os.popen('git rev-parse HEAD').read().strip()
        os.system("git commit -m 'Version: 2024_02' --allow-empty")

        finder = VersionFinder(path=test_repo)
        prev_version, next_version = finder.get_commit_surrounding_versions(middle_commit)

        assert finder.get_version_from_commit(prev_version) == '2024_01'
        assert finder.get_version_from_commit(next_version) == '2024_02'

    def test_repository_not_clean(self, test_repo):
        # Create uncommitted changes
        with open(f"{test_repo}/file1", "w") as f:
            f.write("modified content")

        with pytest.raises(GitRepositoryNotClean):
            VersionFinder(path=test_repo, logger=debug_logger)

    def test_custom_config(self, test_repo):
        config = GitConfig(
            timeout=60,
            max_retries=3,
            retry_delay=2,
        )
        finder = VersionFinder(path=test_repo, config=config)
        assert finder.config.timeout == 60
        assert finder.config.max_retries == 3
        assert finder.config.retry_delay == 2

    @pytest.fixture
    def repo_with_submodule(self, test_repo):
        # Create a separate repo to use as a submodule
        sub_dir = os.path.join(test_repo, "sub_repo")
        os.makedirs(sub_dir)
        os.chdir(sub_dir)
        os.system("git init")
        os.system("git config user.email 'test@example.com'")
        os.system("git config user.name 'Test User'")
        os.system("touch sub_file")
        os.system("git add sub_file")
        os.system("git commit -m 'Submodule initial commit'")

        # Add submodule to main repo
        os.chdir(test_repo)
        os.system(f"git submodule add {sub_dir}")
        os.system(f"git commit -m 'Add submodule {sub_dir}'")

        yield test_repo

        os.system(f"rm -rf {sub_dir}")

    def test_get_first_commit_including_submodule_changes(self, repo_with_submodule):
        # This test verifies that the VersionFinder can correctly identify the first commit
        # that includes changes in the submodule
        finder = VersionFinder(path=repo_with_submodule)

        # Choose a branch to update the repository to
        update_repository_branch = 'main'
        finder.update_repository(update_repository_branch)

        # Call get_first_commit_including_submodule_changes() to retrieve the first commit
        first_commit = finder.get_first_commit_including_submodule_changes('sub_repo', 'HEAD')
        # Verify that the first commit is correct
        assert first_commit == os.popen('git rev-parse HEAD').read().strip()

    def test_list_submodules(self, repo_with_submodule):
        # This test verifies that the VersionFinder can correctly identify Git submodules
        # It uses the repo_with_submodule fixture which creates a test repo containing a submodule named 'sub1'
        finder = VersionFinder(path=repo_with_submodule)
        # Call list_submodules() to retrieve list of submodules in the repository
        submodules = finder.list_submodules()
        # Verify that the 'sub1' submodule is found in the list of submodules
        assert 'sub_repo' in submodules

    def test_list_submodules_empty(self, test_repo):
        # This test verifies that the VersionFinder can correctly handle the case where there are no submodules
        # It uses the test_repo fixture which creates a test repo without any submodules
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        # Call list_submodules() to retrieve list of submodules in the repository
        submodules = finder.list_submodules()
        # Verify that the list of submodules is empty
        assert len(submodules) == 0

    def test_list_submodules_invalid_repo(self, test_repo):
        # This test verifies that the VersionFinder can correctly handle the case where the repository is invalid
        # It uses the test_repo fixture which creates a test repo without any submodules
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        # Call list_submodules() to retrieve list of submodules in the repository
        submodules = finder.list_submodules()
        # Verify that the list of submodules is empty
        assert len(submodules) == 0

    def test_get_submodule_commit_hash(self, repo_with_submodule):
        finder = VersionFinder(path=repo_with_submodule)

        finder.update_repository('main')
        # Call get_submodule_commit_hash() to retrieve the submodule pointer from a specific commit
        submodule_ptr = finder.get_submodule_commit_hash('HEAD', 'sub_repo')
        # Verify that the submodule pointer is correct

        # change dir to submodule
        os.chdir(os.path.join(repo_with_submodule, 'sub_repo'))

        # get head commit
        head_commit = os.popen('git rev-parse HEAD').read().strip()
        assert submodule_ptr == head_commit

    @pytest.fixture
    def repo_with_versions(self, test_repo):
        # Add commits with different versions
        os.chdir(test_repo)
        os.system("git checkout main")
        os.system("git commit -m 'Version: 1_0_0' --allow-empty")
        os.system("touch file2")
        os.system("git add file2")
        os.system("git commit -m 'add file2")
        os.system("git commit -m 'Version: 1_1_0' --allow-empty")

        yield test_repo

    def test_find_commit_by_version(self, repo_with_versions):
        finder = VersionFinder(path=repo_with_versions)
        finder.update_repository('main')
        commits = finder.find_commit_by_version('1_0_0')
        assert len(commits) == 1
        assert commits[0] == os.popen('git rev-parse HEAD~1').read().strip()

        commits = finder.find_commit_by_version('1_1_0')
        assert len(commits) == 1
        assert commits[0] == os.popen('git rev-parse HEAD').read().strip()

    def test_find_commits_by_text_basic(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        finder.update_repository('main')

        # Create test commits with specific text
        os.chdir(test_repo)
        os.system("git commit -m 'Test message one' --allow-empty")
        first_commit = os.popen('git rev-parse HEAD').read().strip()
        os.system("git commit -m 'Different message' --allow-empty")
        os.system("git commit -m 'Test message two' --allow-empty")
        second_commit = os.popen('git rev-parse HEAD').read().strip()

        # Test finding commits with text
        commits = finder.find_commits_by_text("Test message")
        assert len(commits) == 2
        assert first_commit in commits
        assert second_commit in commits

    def test_find_commits_by_text_case_insensitive(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        finder.update_repository('main')

        os.chdir(test_repo)
        os.system("git commit -m 'UPPER CASE MESSAGE' --allow-empty")
        commit_hash = os.popen('git rev-parse HEAD').read().strip()

        commits = finder.find_commits_by_text("upper case")
        assert len(commits) == 1
        assert commit_hash in commits

    def test_find_commits_by_text_in_submodule(self, repo_with_submodule):
        finder = VersionFinder(path=repo_with_submodule, logger=debug_logger)
        finder.update_repository('main')

        # Add commit in submodule
        os.chdir(os.path.join(repo_with_submodule, 'sub_repo'))
        os.system("git commit -m 'Submodule specific text' --allow-empty")
        submodule_commit = os.popen('git rev-parse HEAD').read().strip()

        commits = finder.find_commits_by_text("Submodule specific", submodule='sub_repo')
        assert len(commits) == 1
        assert submodule_commit in commits

    def test_find_commits_by_text_no_matches(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        finder.update_repository('main')

        commits = finder.find_commits_by_text("NonexistentText")
        assert len(commits) == 0

    def test_find_commits_by_text_invalid_submodule(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        finder.update_repository('main')

        with pytest.raises(GitCommandError):
            finder.find_commits_by_text("test", submodule="nonexistent-submodule")

    def test_find_commits_by_text_repository_not_ready(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=debug_logger)
        # Don't call update_repository to test not ready state

        with pytest.raises(ValueError, match="Repository is not ready to perform tasks."):
            finder.find_commits_by_text("test")
