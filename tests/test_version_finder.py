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

logger = setup_logger(__name__, level=logging.DEBUG)


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
        finder = VersionFinder(path=test_repo, logger=logger)
        assert finder.repository_path == Path(test_repo).resolve()
        assert isinstance(finder.config, GitConfig)

    def test_init_invalid_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(InvalidGitRepository):
                VersionFinder(path=temp_dir)

    def test_get_branches(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=logger)
        branches = finder.get_branches()
        assert 'main' in branches or 'master' in branches
        assert 'dev' in branches
        assert 'feature' in branches

    def test_is_valid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=logger)
        assert finder.is_valid_branch('dev')
        assert not finder.is_valid_branch('nonexistent-branch')

    def test_update_repository_valid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=logger)
        finder.update_repository('dev')
        # Verify we're on dev branch
        result = os.popen('git branch --show-current').read().strip()
        assert result == 'dev'

    def test_update_repository_invalid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo, logger=logger)
        with pytest.raises(GitCommandError):
            finder.update_repository('nonexistent-branch')

    def test_repository_not_clean(self, test_repo):
        # Create uncommitted changes
        with open(f"{test_repo}/file1", "w") as f:
            f.write("modified content")

        with pytest.raises(GitRepositoryNotClean):
            VersionFinder(path=test_repo, logger=logger)

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

    def test_get_submodules(self, repo_with_submodule):
        # This test verifies that the VersionFinder can correctly identify Git submodules
        # It uses the repo_with_submodule fixture which creates a test repo containing a submodule named 'sub1'
        finder = VersionFinder(path=repo_with_submodule)
        # Call get_submodules() to retrieve list of submodules in the repository
        submodules = finder.get_submodules()
        # Verify that the 'sub1' submodule is found in the list of submodules
        assert 'sub_repo' in submodules

    def test_get_submodules_empty(self, test_repo):
        # This test verifies that the VersionFinder can correctly handle the case where there are no submodules
        # It uses the test_repo fixture which creates a test repo without any submodules
        finder = VersionFinder(path=test_repo, logger=logger)
        # Call get_submodules() to retrieve list of submodules in the repository
        submodules = finder.get_submodules()
        # Verify that the list of submodules is empty
        assert len(submodules) == 0

    def test_get_submodules_invalid_repo(self, test_repo):
        # This test verifies that the VersionFinder can correctly handle the case where the repository is invalid
        # It uses the test_repo fixture which creates a test repo without any submodules
        finder = VersionFinder(path=test_repo, logger=logger)
        # Call get_submodules() to retrieve list of submodules in the repository
        submodules = finder.get_submodules()
        # Verify that the list of submodules is empty
        assert len(submodules) == 0

    def test_get_submodule_ptr_from_commit(self, repo_with_submodule):
        finder = VersionFinder(path=repo_with_submodule)
        # Call get_submodule_ptr_from_commit() to retrieve the submodule pointer from a specific commit
        submodule_ptr = finder.get_submodule_ptr_from_commit('main', 'sub_repo')
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
        os.system("git commit -m 'VERSION: 1_0_0' --allow-empty")
        os.system("touch file2")
        os.system("git add file2")
        os.system("git commit -m 'add file2")
        os.system("git commit -m 'VERSION: 1_1_0' --allow-empty")

        yield test_repo

    def test_find_version_commit(self, repo_with_versions):
        finder = VersionFinder(path=repo_with_versions)
        commits = finder.find_version_commit('main', '1_0_0')
        assert len(commits) == 1
        assert commits[0] == os.popen('git rev-parse HEAD~1').read().strip()

        commits = finder.find_version_commit('main', '1_1_0')
        assert len(commits) == 1
        assert commits[0] == os.popen('git rev-parse HEAD').read().strip()
