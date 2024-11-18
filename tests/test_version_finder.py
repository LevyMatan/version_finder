import pytest
import os
import tempfile
from pathlib import Path
from version_finder.core import (
    VersionFinder,
    GitConfig,
    InvalidGitRepository,
    GitRepositoryNotClean,
    GitCommandError
)


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
        finder = VersionFinder(path=test_repo)
        assert finder.repository_path == Path(test_repo).resolve()
        assert isinstance(finder.config, GitConfig)

    def test_init_invalid_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(InvalidGitRepository):
                VersionFinder(path=temp_dir)

    def test_get_branches(self, test_repo):
        finder = VersionFinder(path=test_repo)
        branches = finder.get_branches()
        assert 'main' in branches or 'master' in branches
        assert 'dev' in branches
        assert 'feature' in branches

    def test_is_valid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo)
        assert finder.is_valid_branch('dev')
        assert not finder.is_valid_branch('nonexistent-branch')

    def test_update_repository_valid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo)
        finder.update_repository('dev')
        # Verify we're on dev branch
        result = os.popen('git branch --show-current').read().strip()
        assert result == 'dev'

    def test_update_repository_invalid_branch(self, test_repo):
        finder = VersionFinder(path=test_repo)
        with pytest.raises(GitCommandError):
            finder.update_repository('nonexistent-branch')

    def test_repository_not_clean(self, test_repo):
        # Create uncommitted changes
        with open(f"{test_repo}/file1", "w") as f:
            f.write("modified content")

        with pytest.raises(GitRepositoryNotClean):
            VersionFinder(path=test_repo)

    def test_custom_config(self, test_repo):
        config = GitConfig(
            timeout=60,
            max_retries=3,
            retry_delay=2,
            parallel_submodule_fetch=False
        )
        finder = VersionFinder(path=test_repo, config=config)
        assert finder.config.timeout == 60
        assert finder.config.max_retries == 3
        assert finder.config.retry_delay == 2
        assert finder.config.parallel_submodule_fetch is False

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