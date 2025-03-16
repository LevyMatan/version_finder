import pytest
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch
from version_finder.version_finder import (
    VersionFinder,
    InvalidGitRepository,
    GitRepositoryNotClean,
    RepositoryNotTaskReady,
    InvalidCommitError,
    InvalidSubmoduleError,
    InvalidBranchError,
    VersionNotFoundError,
    InvalidFilepathError,
    Commit,
    GitConfig
)
from version_finder.logger import (
    get_logger,
)


debug_logger = get_logger(__name__, verbose=True)


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


class TestCommit:
    def test_commit_str_representation(self):
        commit = Commit(
            sha="abc123def456",
            subject="Test commit",
            message="Full test commit message",
            author="John Doe",
            timestamp=1234567890
        )
        expected = "abc123def456    Test commit"
        assert str(commit) == expected

    def test_commit_repr_representation(self):
        commit = Commit(
            sha="abc123def456",
            subject="Test commit",
            message="Full test commit message",
            author="John Doe",
            timestamp=1234567890
        )
        expected = "Commit(sha=abc123def456    subject=Test commit)"
        assert repr(commit) == expected

    def test_commit_with_version(self):
        commit = Commit(
            sha="abc123def456",
            subject="Test commit",
            message="Full test commit message",
            author="John Doe",
            timestamp=1234567890,
            version="1.0.0"
        )
        assert commit.version == "1.0.0"


class TestVersionFinder:
    @pytest.fixture
    def test_repo(self):
        """Creates a temporary test repository with initial commit"""
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)

        # Initialize repo and create initial commit
        os.system('git init')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        # Replace touch with Python file creation
        with open(os.path.join(temp_dir, "file1"), "w") as f:
            pass
        os.system('git add file1')
        os.system('git commit -m "Initial commit"')

        # Get the default branch name (could be main or master depending on git version)
        default_branch = os.popen("git branch --show-current").read().strip()

        # Create test branches
        os.system('git branch dev')
        os.system('git branch feature')

        yield temp_dir, default_branch

        # Cleanup - use shutil instead of rm -rf
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_init_valid_repository(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        print(f"Type of finder.config: {type(finder.config)}")
        print(f"Type of GitConfig: {type(GitConfig)}")
        print(f"GitConfig MRO: {GitConfig.__mro__}")
        assert finder.repository_path == Path(test_repo[0]).resolve()
        assert isinstance(finder.config, GitConfig)

    def test_init_invalid_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(InvalidGitRepository):
                VersionFinder(path=temp_dir)

    def test_list_branches(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        branches = finder.list_branches()
        assert 'main' in branches or 'master' in branches
        assert 'dev' in branches
        assert 'feature' in branches

    def test_has_branch(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        assert finder.has_branch('dev')
        assert not finder.has_branch('nonexistent-branch')

    def test_update_repository_valid_branch(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository('dev')
        # Verify we're on dev branch
        result = os.popen('git branch --show-current').read().strip()
        assert result == 'dev'

    def test_update_repository_invalid_branch(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        with pytest.raises(InvalidBranchError):
            finder.update_repository('nonexistent-branch')

    def test_get_current_branch(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])

        # Test getting current branch on main
        current_branch = finder.get_current_branch()
        assert current_branch in ['main', 'master']

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

    def test_extract_version_from_message(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])

        # Test various version formats
        test_cases = [
            ("Version: 2024_01", "2024_01"),
            ("Version: XX_2024_01_15", "2024_01_15"),
            ("Random text Version: 2024-01-15 more text", "2024-01-15"),
            ("2024_01_15_23", "2024_01_15_23"),
            ("Version: XX_2024_01", "2024_01"),
            ("No version here", None),
            ("Version: XX_2024_01_15_RC1", "2024_01_15"),
            ("Version: 2024_01-15", "2024_01-15"),
            ("Updated version 1.1.1", "1.1.1"),
            ("Updated version 1.133.1123", "1.133.1123"),
        ]

        for message, expected in test_cases:
            result = finder._VersionFinder__extract_version_from_message(message)
            assert result == expected, f"Failed for message: {message}"

    def test_find_first_version_containing_commit_basic(self, test_repo: tuple[str, str]):
        # Setup test repository with version commits
        os.chdir(test_repo[0])
        os.system(f'git checkout {test_repo[1]}')
        os.system('git commit -m "Initial commit" --allow-empty')
        commit_to_find = os.popen('git rev-parse HEAD').read().strip()
        os.system('git commit -m "Version: 2024_01" --allow-empty')

        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        version = finder.find_first_version_containing_commit(commit_to_find)
        assert version == '2024_01'

    def test_find_first_version_containing_commit_multiple_versions(self, test_repo: tuple[str, str]):
        os.chdir(test_repo[0])
        os.system(f'git checkout {test_repo[1]}')
        os.system('git commit -m "Version: 2024_01" --allow-empty')
        os.system('git commit -m "Some commit" --allow-empty')
        commit_to_find = os.popen('git rev-parse HEAD').read().strip()
        os.system('git commit -m "Version: 2024_02" --allow-empty')
        os.system('git commit -m "Version: 2024_03" --allow-empty')

        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        version = finder.find_first_version_containing_commit(commit_to_find)
        assert version == '2024_02'

    def test_find_first_version_containing_commit_with_submodule(self, repo_with_submodule: tuple[str, str]):
        # Setup submodule with specific commit
        os.chdir(os.path.join(repo_with_submodule[0], 'sub_repo'))
        os.system('git commit -m "Submodule commit" --allow-empty')
        submodule_commit = os.popen('git rev-parse HEAD').read().strip()

        # Update main repo with version
        os.chdir(repo_with_submodule[0])
        os.system('git add sub_repo')
        os.system('git commit -m "Version: 2024_01" --allow-empty')

        finder = VersionFinder(path=repo_with_submodule[0])
        finder.update_repository(repo_with_submodule[1])
        version = finder.find_first_version_containing_commit(submodule_commit, submodule='sub_repo')
        assert version == '2024_01'

    def test_find_first_version_containing_commit_nonexistent_commit(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        with pytest.raises(InvalidCommitError, match="Commit nonexistent-commit does not exist"):
            finder.update_repository(test_repo[1])
            finder.find_first_version_containing_commit('nonexistent-commit')

    def test_find_first_version_containing_commit_no_version_after(self, test_repo: tuple[str, str]):
        os.chdir(test_repo[0])
        os.system('git checkout main')
        os.system('git commit -m "Version: 2024_01" --allow-empty')
        os.system('git commit -m "Latest commit" --allow-empty')
        commit_to_find = os.popen('git rev-parse HEAD').read().strip()

        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        version = finder.find_first_version_containing_commit(commit_to_find)
        assert version is None

    def test_get_commit_surrounding_versions(self, test_repo: tuple[str, str]):
        os.chdir(test_repo[0])
        os.system('git checkout main')
        os.system('git commit -m "Version: 2024_01" --allow-empty')
        os.system('git commit -m "Middle commit" --allow-empty')
        middle_commit = os.popen('git rev-parse HEAD').read().strip()
        os.system('git commit -m "Version: 2024_02" --allow-empty')

        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        prev_version, next_version = finder.get_commit_surrounding_versions(middle_commit)

        assert finder.get_version_from_commit(prev_version) == '2024_01'
        assert finder.get_version_from_commit(next_version) == '2024_02'

    def test_repository_not_clean(self, test_repo: tuple[str, str]):
        # Create uncommitted changes
        with open(f"{test_repo[0]}/file1", "w") as f:
            f.write("modified content")

        with pytest.raises(GitRepositoryNotClean):
            VersionFinder(path=test_repo[0])

    def test_custom_config(self, test_repo: tuple[str, str]):
        config = GitConfig(
            timeout=60,
            max_retries=3,
            retry_delay=2,
        )
        finder = VersionFinder(path=test_repo[0], config=config)
        assert finder.config.timeout == 60
        assert finder.config.max_retries == 3
        assert finder.config.retry_delay == 2

    @pytest.fixture
    def repo_with_submodule(self, test_repo: tuple[str, str]):
        # Create a separate repo to use as a submodule
        sub_dir = os.path.join(test_repo[0], "sub_repo")
        os.makedirs(sub_dir)
        os.chdir(sub_dir)
        os.system('git init')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        # Replace touch with Python file creation
        with open(os.path.join(sub_dir, "sub_file"), "w") as f:
            pass
        os.system('git add sub_file')
        os.system('git commit -m "Submodule initial commit"')

        # Add submodule to main repo
        os.chdir(test_repo[0])
        os.system(f'git submodule add {sub_dir}')
        os.system(f'git commit -m "Add submodule {sub_dir}"')

        yield test_repo

        # Cleanup handled by test_repo fixture

    def test_get_first_commit_including_submodule_changes(self, repo_with_submodule: tuple[str, str]):
        # This test verifies that the VersionFinder can correctly identify the first commit
        # that includes changes in the submodule
        finder = VersionFinder(path=repo_with_submodule[0])

        # Choose a branch to update the repository to
        update_repository_branch = repo_with_submodule[1]
        finder.update_repository(update_repository_branch)

        # Call get_first_commit_including_submodule_changes() to retrieve the first commit
        first_commit = finder.get_first_commit_including_submodule_changes('sub_repo', 'HEAD')
        # Verify that the first commit is correct
        assert first_commit == os.popen('git rev-parse HEAD').read().strip()

    def test_list_submodules(self, repo_with_submodule: Any):
        # This test verifies that the VersionFinder can correctly identify Git submodules
        # It uses the repo_with_submodule fixture which creates a test repo containing a submodule named 'sub1'
        finder = VersionFinder(path=repo_with_submodule[0])
        # Call list_submodules() to retrieve list of submodules in the repository
        submodules = finder.list_submodules()
        # Verify that the 'sub1' submodule is found in the list of submodules
        assert 'sub_repo' in submodules

    def test_list_submodules_empty(self, test_repo: tuple[str, str]):
        # This test verifies that the VersionFinder can correctly handle the case where there are no submodules
        # It uses the test_repo fixture which creates a test repo without any submodules
        finder = VersionFinder(path=test_repo[0])
        # Call list_submodules() to retrieve list of submodules in the repository
        submodules = finder.list_submodules()
        # Verify that the list of submodules is empty
        assert len(submodules) == 0

    def test_list_submodules_invalid_repo(self, test_repo: tuple[str, str]):
        # This test verifies that the VersionFinder can correctly handle the case where the repository is invalid
        # It uses the test_repo fixture which creates a test repo without any submodules
        finder = VersionFinder(path=test_repo[0])
        # Call list_submodules() to retrieve list of submodules in the repository
        submodules = finder.list_submodules()
        # Verify that the list of submodules is empty
        assert len(submodules) == 0

    def test_get_submodule_commit_hash(self, repo_with_submodule: tuple[str, str]):
        finder = VersionFinder(path=repo_with_submodule[0])

        finder.update_repository(repo_with_submodule[1])
        # Call get_submodule_commit_hash() to retrieve the submodule pointer from a specific commit
        submodule_ptr = finder.get_submodule_commit_hash('HEAD', 'sub_repo')
        # Verify that the submodule pointer is correct

        # change dir to submodule
        os.chdir(os.path.join(repo_with_submodule[0], 'sub_repo'))

        # get head commit
        head_commit = os.popen('git rev-parse HEAD').read().strip()
        assert submodule_ptr == head_commit

    @pytest.fixture
    def repo_with_versions(self, test_repo: tuple[str, str]):
        # Add commits with different versions
        os.chdir(test_repo[0])
        # Get the default branch name
        default_branch = os.popen("git branch --show-current").read().strip()
        os.system(f'git checkout {default_branch}')
        os.system('git commit -m "Version: 1_0_0" --allow-empty')
        # Replace touch with Python file creation
        with open(os.path.join(test_repo[0], "file2"), "w") as f:
            pass
        os.system('git add file2')
        os.system('git commit -m "add file2"')
        os.system('git commit -m "Version: 1_1_0" --allow-empty')

        yield test_repo

    def test_find_commit_by_version(self, repo_with_versions: tuple[str, str]):
        finder = VersionFinder(path=repo_with_versions[0])
        finder.update_repository(repo_with_versions[1])
        commits = finder.find_commit_by_version('1_0_0')
        assert len(commits) == 1
        assert commits[0] == os.popen('git rev-parse HEAD~2').read().strip()

        commits = finder.find_commit_by_version('1_1_0')
        assert len(commits) == 1
        assert commits[0] == os.popen('git rev-parse HEAD').read().strip()

    def test_find_commits_by_text_basic(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])

        # Create test commits with specific text
        os.chdir(test_repo[0])
        os.system('git commit -m "Test message one" --allow-empty')
        first_commit = os.popen('git rev-parse HEAD').read().strip()
        os.system('git commit -m "Different message" --allow-empty')
        os.system('git commit -m "Test message two" --allow-empty')
        second_commit = os.popen('git rev-parse HEAD').read().strip()

        # Test finding commits with text
        commits = finder.find_commits_by_text("Test message")
        commit_shas = [commit.sha for commit in commits]
        assert len(commits) == 2
        assert first_commit in commit_shas
        assert second_commit in commit_shas

    def test_find_commits_by_text_case_insensitive(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])

        os.chdir(test_repo[0])
        os.system('git commit -m "UPPER CASE MESSAGE" --allow-empty')
        commit_hash = os.popen('git rev-parse HEAD').read().strip()

        commits = finder.find_commits_by_text("upper case")
        assert len(commits) == 1
        assert commit_hash in commits[0].sha

    def test_find_commits_by_text_in_submodule(self, repo_with_submodule: tuple[str, str]):
        finder = VersionFinder(path=repo_with_submodule[0])
        finder.update_repository(repo_with_submodule[1])

        # Add commit in submodule
        os.chdir(os.path.join(repo_with_submodule[0], 'sub_repo'))
        os.system('git commit -m "Submodule specific text" --allow-empty')
        submodule_commit = os.popen('git rev-parse HEAD').read().strip()

        commits = finder.find_commits_by_text("Submodule specific", submodule='sub_repo')
        assert len(commits) == 1
        assert submodule_commit == commits[0].sha

    def test_find_commits_by_text_no_matches(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])

        commits = finder.find_commits_by_text("NonexistentText")
        assert len(commits) == 0

    def test_find_commits_by_text_invalid_submodule(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])

        with pytest.raises(InvalidSubmoduleError):
            finder.find_commits_by_text("test", submodule="nonexistent-submodule")

    def test_find_commits_by_text_repository_not_ready(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        # Don't call update_repository to test not ready state

        with pytest.raises(RepositoryNotTaskReady):
            finder.find_commits_by_text("test")

    def test_get_commits_between_versions(self, test_repo: tuple[str, str]):
        # Setup test repository with version commits
        os.chdir(test_repo[0])
        os.system('git checkout main')
        os.system('git commit -m "Version: 2024_01" --allow-empty')
        os.system('git commit -m "Intermediate commit 1" --allow-empty')
        os.system('git commit -m "Intermediate commit 2" --allow-empty')
        os.system('git commit -m "Version: 2024_02" --allow-empty')

        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        commits = finder.get_commits_between_versions('2024_01', '2024_02')
        commits_shas = [commit.sha for commit in commits]
        # Verify we got the intermediate commits
        assert len(commits) == 4

        # Verify commit messages
        for commit in commits_shas:
            message = os.popen(f'git log -1 --format=%s {commit}').read().strip()
            assert message in ['Version: 2024_01', 'Intermediate commit 1', 'Intermediate commit 2', 'Version: 2024_02']

    def test_get_commits_between_versions_with_submodule(self, repo_with_submodule: tuple[str, str]):
        # Setup submodule with initial commit
        os.chdir(os.path.join(repo_with_submodule[0], 'sub_repo'))
        os.system('git commit -m "Sub commit 1" --allow-empty')
        sub_commit1 = os.popen('git rev-parse HEAD').read().strip()

        # Update main repo with first version pointing to first submodule commit
        os.chdir(repo_with_submodule[0])
        os.system('git add sub_repo')
        os.system('git commit -m "Version: 2024_01"')

        # Create second commit in submodule
        os.chdir(os.path.join(repo_with_submodule[0], 'sub_repo'))
        os.system('git commit -m "Sub commit 2" --allow-empty')
        sub_commit2 = os.popen('git rev-parse HEAD').read().strip()

        # Update main repo to point to new submodule commit
        os.chdir(repo_with_submodule[0])
        os.system('git add sub_repo')
        os.system('git commit -m "Version: 2024_02"')

        finder = VersionFinder(path=repo_with_submodule[0])
        finder.update_repository(repo_with_submodule[1])
        commits = finder.get_commits_between_versions('2024_01', '2024_02', submodule='sub_repo')
        commits_shas = [commit.sha for commit in commits]
        # Verify we got the submodule commit
        assert len(commits) == 2
        assert sub_commit1 in commits_shas
        assert sub_commit2 in commits_shas

    def test_get_commits_between_versions_invalid_version(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        with pytest.raises(VersionNotFoundError):
            _ = finder.get_commits_between_versions('nonexistent_version1', 'nonexistent_version2')

    def test_get_commits_between_versions_not_ready(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        # Don't call update_repository to test not ready state
        with pytest.raises(RepositoryNotTaskReady):
            finder.get_commits_between_versions('2024_01', '2024_02')

    def test_get_commit_info_basic(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        os.chdir(test_repo[0])
        os.system('git commit -m "Version: 2024_01" --allow-empty')
        commit_sha = os.popen('git rev-parse HEAD').read().strip()

        finder.update_repository(test_repo[1])
        commit_info = finder.get_commit_info(commit_sha)
        assert commit_info.sha == commit_sha
        assert commit_info.subject == 'Version: 2024_01'
        assert commit_info.version == '2024_01'
        assert isinstance(commit_info.timestamp, int)
        assert commit_info.author == 'Test User'

    def test_get_commit_info_with_multiline_message(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        os.chdir(test_repo[0])
        # For multiline commit messages, use a temporary file instead
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as f:
            f.write("""Version: 2024_02

            This is a detailed commit message
            with multiple lines""")
            msg_file = f.name

        try:
            os.system(f'git commit --allow-empty -F "{msg_file}"')
        finally:
            os.unlink(msg_file)  # Clean up the temporary file
        commit_sha = os.popen('git rev-parse HEAD').read().strip()

        finder.update_repository(test_repo[1])
        commit_info = finder.get_commit_info(commit_sha)
        assert commit_info.sha == commit_sha
        assert commit_info.subject == 'Version: 2024_02'
        assert commit_info.version == '2024_02'
        assert 'detailed commit message' in commit_info.message

    def test_get_commit_info_no_version(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        os.chdir(test_repo[0])
        os.system('git commit -m "Regular commit without version" --allow-empty')
        commit_sha = os.popen('git rev-parse HEAD').read().strip()

        finder.update_repository(test_repo[1])
        commit_info = finder.get_commit_info(commit_sha)
        assert commit_info.sha == commit_sha
        assert commit_info.subject == 'Regular commit without version'
        assert commit_info.version is None

    def test_get_commit_info_with_different_version_formats(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        os.chdir(test_repo[0])

        test_cases = [
            ("Version: XX_2024_01_15", "2024_01_15"),
            ("Updated version 1.2.3", "1.2.3"),
            ("Version: 2024-01-15", "2024-01-15"),
            ("Version: 2024_01_15_RC1", "2024_01_15")
        ]

        for message, expected_version in test_cases:
            os.system(f'git commit -m "{message}" --allow-empty')
            commit_sha = os.popen('git rev-parse HEAD').read().strip()
            finder.update_repository(test_repo[1])
            commit_info = finder.get_commit_info(commit_sha)
            assert commit_info.version == expected_version

    def test_get_commit_info_invalid_commit(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        with pytest.raises(InvalidCommitError):
            finder.get_commit_info("nonexistent-commit-sha")

    def test_get_commit_info_not_ready(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        # Don't call update_repository to test not ready state
        with pytest.raises(RepositoryNotTaskReady):
            finder.get_commit_info("nonexistent-commit-sha")


class TestGetCommitDiffFiles:

    @pytest.fixture
    def test_repo(self):
        """Creates a temporary test repository with initial commit"""
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)

        # Initialize repo and create initial commit
        os.system('git init')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        # Replace touch with Python file creation
        with open(os.path.join(temp_dir, "file1"), "w") as f:
            pass
        os.system('git add file1')
        os.system('git commit -m "Initial commit"')

        # Get the default branch name (could be main or master depending on git version)
        default_branch = os.popen("git branch --show-current").read().strip()

        # Create test branches
        os.system('git branch dev')
        os.system('git branch feature')

        yield temp_dir, default_branch

        # Cleanup - use shutil instead of rm -rf
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def setup_repo(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        return finder, test_repo

    def test_get_commit_diff_files_empty_commit_hash(self, setup_repo: tuple[VersionFinder, tuple[str, str]]):
        """Test get_commit_diff_files with an empty commit hash"""
        finder, _ = setup_repo
        with pytest.raises(TypeError):
            finder.get_commit_diff_files('')

    def test_get_commit_diff_files_incorrect_type(self, setup_repo: tuple[VersionFinder, tuple[str, str]]):
        """Test get_commit_diff_files with incorrect input type"""
        finder, _ = setup_repo
        with pytest.raises(TypeError):
            finder.get_commit_diff_files(123)

    # def test_get_commit_diff_files_initial_commit(self, setup_repo):
    #     """Test get_commit_diff_files for the initial commit"""
    #     finder, repo_path = setup_repo
    #     initial_commit = os.popen(f'git -C {repo_path} rev-list --max-parents=0 HEAD').read().strip()
    #     with pytest.raises(InvalidCommitError):
    #         finder.get_commit_diff_files(initial_commit)

    def test_get_commit_diff_files_invalid_commit_hash(self, setup_repo: tuple[VersionFinder, tuple[str, str]]):
        """Test get_commit_diff_files with an invalid commit hash"""
        finder, _ = setup_repo
        with pytest.raises(InvalidCommitError):
            finder.get_commit_diff_files('invalid_commit_hash')

    def test_get_commit_diff_files_invalid_submodule(self, setup_repo: tuple[VersionFinder, tuple[str, str]]):
        """Test get_commit_diff_files with an invalid submodule"""
        finder, _ = setup_repo
        with pytest.raises(InvalidSubmoduleError):
            finder.get_commit_diff_files('HEAD', submodule='nonexistent_submodule')

    def test_get_commit_diff_files_merge_commit(self, setup_repo: tuple[VersionFinder, tuple[str, str]]):
        """Test get_commit_diff_files for a merge commit"""
        finder, repo_path = setup_repo
        # Create a new branch with a new file using Python
        current_dir = os.getcwd()
        try:
            os.chdir(repo_path[0])
            # Get the default branch name
            default_branch = os.popen("git branch --show-current").read().strip()
            os.system('git checkout -b test_branch')
            with open("new_file", "w") as f:
                pass
            os.system('git add new_file')
            os.system('git commit -m "New file in test branch"')
            os.system(f'git checkout {default_branch}')
            os.system('git merge --no-ff test_branch')
            merge_commit = os.popen('git rev-parse HEAD').read().strip()
        finally:
            os.chdir(current_dir)

        diff_files = finder.get_commit_diff_files(merge_commit)
        assert 'new_file' in diff_files

    def test_get_commit_diff_files_repository_not_ready(self, test_repo: tuple[str, str]):
        """Test get_commit_diff_files when repository is not ready"""
        finder = VersionFinder(path=test_repo[0])
        # Don't call update_repository to test not ready state
        with pytest.raises(RepositoryNotTaskReady):
            finder.get_commit_diff_files('HEAD')

    # def test_get_commit_diff_files_with_rename(self, setup_repo):
    #     """Test get_commit_diff_files for a commit with renamed file"""
    #     finder, repo_path = setup_repo
    #     os.system(f"cd {repo_path} && mv file1 file1_renamed && git add . && git commit -m 'Renamed file1'")
    #     rename_commit = os.popen(f'git -C {repo_path} rev-parse HEAD').read().strip()
    #     diff_files = finder.get_commit_diff_files(rename_commit)
    #     assert 'file1' in diff_files
    #     assert 'file1_renamed' in diff_files
    #


class TestVersionFinderNegative:

    @pytest.fixture
    def test_repo(self):
        """Creates a temporary test repository with initial commit"""
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)

        # Initialize repo and create initial commit
        os.system('git init')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        # Replace touch with Python file creation
        with open(os.path.join(temp_dir, "file1"), "w") as f:
            pass
        os.system('git add file1')
        os.system('git commit -m "Initial commit"')

        # Get the default branch name (could be main or master depending on git version)
        default_branch = os.popen("git branch --show-current").read().strip()

        # Create test branches
        os.system('git branch dev')
        os.system('git branch feature')

        yield temp_dir, default_branch

        # Cleanup - use shutil instead of rm -rf
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def setup_repo(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        return finder, test_repo

    def test_get_file_content_at_commit_empty_commit_hash(self, version_finder: VersionFinder):
        """Test get_file_content_at_commit with empty commit hash."""
        with pytest.raises(TypeError):
            version_finder.get_file_content_at_commit("", "file.txt")

    def test_get_file_content_at_commit_empty_file_path(self, version_finder: VersionFinder):
        """Test get_file_content_at_commit with empty file path."""
        with pytest.raises(InvalidFilepathError):
            version_finder.get_file_content_at_commit("HEAD", "")

    # def test_get_file_content_at_commit_file_outside_repository(self, version_finder):
    #     """Test get_file_content_at_commit with file path outside repository."""
    #     with pytest.raises(RuntimeError):
    #         version_finder.get_file_content_at_commit("HEAD", "../outside_repo_file.txt")

    def test_get_file_content_at_commit_incorrect_type(self, version_finder: VersionFinder):
        """Test get_file_content_at_commit with incorrect input types."""
        with pytest.raises(TypeError):
            version_finder.get_file_content_at_commit(123, "file.txt")

    def test_get_file_content_at_commit_invalid_commit_hash(self, version_finder: VersionFinder):
        """Test get_file_content_at_commit with invalid commit hash."""
        with pytest.raises(InvalidCommitError):
            version_finder.get_file_content_at_commit("invalid_hash", "file.txt")

    def test_get_file_content_at_commit_invalid_submodule(self, version_finder: VersionFinder):
        """Test get_file_content_at_commit with invalid submodule."""
        with pytest.raises(InvalidSubmoduleError):
            version_finder.get_file_content_at_commit("HEAD", "file.txt", submodule="invalid_submodule")

    def test_get_file_content_at_commit_nonexistent_file(self, version_finder: VersionFinder):
        """Test get_file_content_at_commit with nonexistent file."""
        assert '' == version_finder.get_file_content_at_commit(commit_hash="HEAD", file_path="nonexistent_file.txt")

    def test_get_file_content_at_commit_repository_not_ready(self, test_repo: tuple[str, str]):
        """Test get_file_content_at_commit when repository is not ready."""
        finder = VersionFinder(path=test_repo[0])
        with pytest.raises(RepositoryNotTaskReady):
            finder.get_file_content_at_commit("HEAD", "file.txt")

    @pytest.fixture
    def version_finder(self, test_repo: tuple[str, str]):
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        return finder

    def test_generate_commit_diff_html_empty_commit_hash(self, test_repo: tuple[str, str]):
        """Test generate_commit_diff_html with an empty commit hash."""
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        with pytest.raises(TypeError):
            result = finder.generate_commit_diff_html('')

    def test_generate_commit_diff_html_exception_handling(self, test_repo, monkeypatch):
        """Test exception handling in generate_commit_diff_html."""
        def mock_get_commit_diff_files(*args):
            raise Exception("Mocked exception")

        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        monkeypatch.setattr(finder, 'get_commit_diff_files', mock_get_commit_diff_files)
        result = finder.generate_commit_diff_html('HEAD')
        assert result == 'Error: Mocked exception'

    def test_generate_commit_diff_html_incorrect_type(self, test_repo: tuple[str, str]):
        """Test generate_commit_diff_html with incorrect type for commit_hash."""
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        with pytest.raises(TypeError):
            finder.generate_commit_diff_html(123)

    def test_generate_commit_diff_html_invalid_commit_hash(self, test_repo: tuple[str, str]):
        """Test generate_commit_diff_html with an invalid commit hash."""
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        result = finder.generate_commit_diff_html('invalid_commit_hash')
        assert result.startswith('Error: ')

    def test_generate_commit_diff_html_invalid_output_path(self, test_repo: tuple[str, str]):
        """Test generate_commit_diff_html with an invalid output path."""
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        result = finder.generate_commit_diff_html('HEAD', output_html='/invalid/path/output.html')
        assert result.startswith('Error: ')

    def test_generate_commit_diff_html_invalid_submodule(self, test_repo: tuple[str, str]):
        """Test generate_commit_diff_html with an invalid submodule."""
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        result = finder.generate_commit_diff_html('HEAD', submodule='nonexistent_submodule')
        assert result.startswith('Error: ')

    # def test_generate_commit_diff_html_no_changes(self, test_repo):
    #     """Test generate_commit_diff_html when there are no changes in the commit."""
    #     finder = VersionFinder(path=test_repo)
    #     finder.update_repository('main')
    #     os.system('git commit --allow-empty -m "Empty commit"')
    #     commit_hash = os.popen('git rev-parse HEAD').read().strip()
    #     result = finder.generate_commit_diff_html(commit_hash)
    #     assert 'No changes in this commit' in result

    def test_generate_commit_diff_html_nonexistent_commit(self, test_repo: tuple[str, str]):
        """Test generate_commit_diff_html with a nonexistent commit hash."""
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        result = finder.generate_commit_diff_html('1234567890abcdef')
        assert result.startswith('Error: ')

    def test_generate_commit_diff_html_repository_not_ready(self, test_repo: tuple[str, str]):
        """Test generate_commit_diff_html when repository is not ready."""
        finder = VersionFinder(path=test_repo[0])
        # Don't call update_repository to test not ready state
        result = finder.generate_commit_diff_html('some_commit_hash')
        assert result.startswith('Error: ')

    def test_get_file_content_at_commit_existing_file(self, test_repo: tuple[str, str]):
        """
        Test getting content of an existing file at a specific commit.
        """
        # Setup
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        commit_hash = "abc123"
        file_path = "test.txt"
        expected_content = b"Test file content"

        # Mock the _git.execute method
        with patch.object(finder, '_git') as mock_git:
            mock_git.execute.return_value = expected_content

            # Call the method
            result = finder.get_file_content_at_commit(commit_hash, file_path)

            # Assertions
            assert result == expected_content
            mock_git.execute.assert_called_with(["show", f"{commit_hash}:{file_path}"])

    def test_get_file_content_at_commit_not_ready(self, test_repo: tuple[str, str]):
        """
        Test getting file content when the repository is not ready for tasks.
        """
        # Setup
        finder = VersionFinder(path=test_repo[0])
        finder.update_repository(test_repo[1])
        finder.is_task_ready = False
        commit_hash = "HEAD"
        file_path = "test.txt"

        # Call the method and check for RepositoryNotTaskReady exception
        with pytest.raises(RepositoryNotTaskReady):
            finder.get_file_content_at_commit(commit_hash, file_path)
