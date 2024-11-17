import os
import subprocess
import random
from pathlib import Path
from datetime import datetime, timedelta

def run_command(command, cwd=None):
    """Execute a git command and return its output"""
    return subprocess.run(command, shell=True, cwd=cwd,
                         capture_output=True, text=True, check=True)

def generate_random_version():
    """Generate a random version number in format XX_XX_XXXX"""
    return f"{random.randint(1,99):02d}_{random.randint(1,99):02d}_{random.randint(1,9999):04d}"

def create_commits_in_branch(repo_path, branch_name, num_commits=1000):
    """Create specified number of commits in a branch"""
    version_file = repo_path / "version.txt"
    data_file = repo_path / "data.txt"
    commit_count = 0

    for i in range(num_commits):
        # Every ~10 commits, create a version commit
        if i % 10 == 0:
            version = generate_random_version()
            version_file.write_text(version)
            run_command("git add version.txt", cwd=repo_path)
            run_command(f"git commit -m 'VERSION: {version}'", cwd=repo_path)
        else:
            # Regular commit with random changes
            data_file.write_text(f"Change {i} in branch {branch_name}\n")
            run_command("git add data.txt", cwd=repo_path)
            run_command(f"git commit -m 'Update {i} in {branch_name}'", cwd=repo_path)

        commit_count += 1
        if commit_count % 100 == 0:
            print(f"Created {commit_count} commits in {branch_name}")

def create_test_repo():
    # Create and initialize a new test repository
    repo_path = Path("test_version_repo")
    if repo_path.exists():
        import shutil
        shutil.rmtree(repo_path)

    repo_path.mkdir()
    print(f"Creating repository at: {repo_path.absolute()}")

    # Initialize git repository
    run_command("git init", cwd=repo_path)
    run_command("git config user.email 'test@example.com'", cwd=repo_path)
    run_command("git config user.name 'Test User'", cwd=repo_path)

    # Create initial commit in master branch
    version_file = repo_path / "version.txt"
    version_file.write_text("00_00_0000")
    run_command("git add version.txt", cwd=repo_path)
    run_command("git commit -m 'Initial commit'", cwd=repo_path)

    # Create 20 branches with ~1000 commits each
    branch_types = ['feature', 'release', 'hotfix', 'development']

    for i in range(20):
        branch_type = random.choice(branch_types)
        branch_name = f"{branch_type}/branch_{i+1}"
        print(f"\nCreating branch: {branch_name}")

        # Create new branch from master
        run_command("git checkout master", cwd=repo_path)
        run_command(f"git checkout -b {branch_name}", cwd=repo_path)

        # Generate commits for this branch
        num_commits = random.randint(900, 1100)  # Random number around 1000
        create_commits_in_branch(repo_path, branch_name, num_commits)

    # Return to master branch
    run_command("git checkout master", cwd=repo_path)

    print("\nRepository creation completed!")
    print("\nBranch structure:")
    print(run_command("git branch", cwd=repo_path).stdout)
    print("\nSample of commit history (last 10 commits):")
    print(run_command("git log --oneline -n 10", cwd=repo_path).stdout)
    print("\nTotal number of commits:")
    print(run_command("git rev-list --all --count", cwd=repo_path).stdout)

if __name__ == "__main__":
    create_test_repo()
