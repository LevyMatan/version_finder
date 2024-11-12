import os
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Execute a git command and return its output"""
    return subprocess.run(command, shell=True, cwd=cwd,
                         capture_output=True, text=True, check=True)

def create_test_repo():
    # Create and initialize a new test repository
    repo_path = Path("test_version_repo")
    if repo_path.exists():
        import shutil
        shutil.rmtree(repo_path)

    repo_path.mkdir()

    # Initialize git repository
    run_command("git init", cwd=repo_path)
    run_command("git config user.email 'test@example.com'", cwd=repo_path)
    run_command("git config user.name 'Test User'", cwd=repo_path)

    # Create initial commit in master branch
    version_file = repo_path / "version.txt"
    version_file.write_text("1.0.0")
    run_command("git add version.txt", cwd=repo_path)
    run_command("git commit -m 'Initial commit with version 1.0.0'", cwd=repo_path)

    # Create and populate feature branch
    run_command("git checkout -b feature/new-feature", cwd=repo_path)
    version_file.write_text("1.1.0-dev")
    run_command("git add version.txt", cwd=repo_path)
    run_command("git commit -m 'Start development of new feature'", cwd=repo_path)

    # Create and populate hotfix branch
    run_command("git checkout master", cwd=repo_path)
    run_command("git checkout -b hotfix/bug-fix", cwd=repo_path)
    version_file.write_text("1.0.1")
    run_command("git add version.txt", cwd=repo_path)
    run_command("git commit -m 'Fix critical bug'", cwd=repo_path)

    # Add some more commits to master branch
    run_command("git checkout master", cwd=repo_path)
    version_file.write_text("1.2.0")
    run_command("git add version.txt", cwd=repo_path)
    run_command("git commit -m 'Bump version to 1.2.0'", cwd=repo_path)

    # Add some tags
    run_command("git tag -a v1.0.0 -m 'Version 1.0.0' HEAD~1", cwd=repo_path)
    run_command("git tag -a v1.2.0 -m 'Version 1.2.0' HEAD", cwd=repo_path)

    print(f"Test repository created at: {repo_path.absolute()}")
    print("\nBranch structure:")
    print(run_command("git branch", cwd=repo_path).stdout)
    print("\nCommit history:")
    print(run_command("git log --oneline --graph --all", cwd=repo_path).stdout)

if __name__ == "__main__":
    create_test_repo()
