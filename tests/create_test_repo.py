import subprocess
import random
from pathlib import Path


def run_command(command, cwd=None):
    """Execute a git command and return its output"""
    return subprocess.run(command, shell=True, cwd=cwd,
                          capture_output=True, text=True, check=True)


def create_commits(repo_path, branch_name, num_commits=1000, is_submodule=False):
    """Create commits in a branch"""
    data_file = repo_path / "data.txt"
    commit_count = 0
    run_command(f"git checkout {branch_name}", cwd=repo_path)

    for i in range(num_commits):
        # Regular commit with random changes
        data_file.write_text(f"Change {i} in branch {branch_name}\n")
        run_command("git add data.txt", cwd=repo_path)
        run_command(f"git commit -m 'Update {i} in {branch_name}'", cwd=repo_path)

        commit_count += 1
        if commit_count % 100 == 0:
            print(f"Created {commit_count} commits in {branch_name}")


def create_submodule(submodule_path):
    """Create and initialize a submodule"""
    if submodule_path.exists():
        import shutil
        shutil.rmtree(submodule_path)
    submodule_path.mkdir()
    run_command("git init", cwd=submodule_path)
    run_command("git config user.email 'submodule@example.com'", cwd=submodule_path)
    run_command("git config user.name 'Submodule User'", cwd=submodule_path)

    # Create initial commit
    data_file = submodule_path / "data.txt"
    data_file.write_text("Initial data")
    run_command("git add data.txt", cwd=submodule_path)
    run_command("git commit -m 'Initial commit in submodule'", cwd=submodule_path)


def update_submodules(main_repo_path, submodules):
    """Periodically update submodules in the main repository"""
    for name, sub_path in submodules.items():
        run_command(f"git submodule add ./{name} {name}", cwd=main_repo_path)
        run_command("git add .gitmodules", cwd=main_repo_path)
        run_command(f"git commit -m 'Add submodule {name}'", cwd=main_repo_path)

import re
from pathlib import Path

def update_version_commit(repo_path, branch):
    repo_path = Path(repo_path)
    version_file = repo_path / "version.txt"

    # Read the current version
    with open(version_file, 'r') as vf:
        version = vf.read().strip()

    # Parse the version into segments
    version_pattern = re.compile(r'^(\d{2})_(\d{2})_(\d{4})$')
    match = version_pattern.match(version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")

    # Extract and convert version segments
    major, minor, patch = map(int, match.groups())

    # Bump the lowest version segment
    patch += 1
    if patch >= 10:
        patch = 0
        minor += 1
        if minor >= 10:
            minor = 0
            major += 1
            if major >= 100:  # Assuming two-digit max for the major segment
                raise ValueError("Version overflow: major segment exceeded maximum")

    # Format the new version
    new_version = f"{major:02}_{minor:02}_{patch:04}"

    # Write the new version to the file
    with open(version_file, 'w') as vf:
        vf.write(new_version)

    # Commit the change using GitPython
    run_command("git add version.txt", cwd=repo_path)
    run_command(f"git commit -m 'Version: {new_version}'", cwd=repo_path)

    print(f"Version updated to {new_version} and committed on branch {branch}.")


def create_test_repo():
    # Main repository
    main_repo_path = Path("test_version_repo")
    if main_repo_path.exists():
        import shutil
        shutil.rmtree(main_repo_path)

    main_repo_path.mkdir()
    print(f"Creating repository at: {main_repo_path.absolute()}")
    run_command("git init", cwd=main_repo_path)
    run_command("git config user.email 'main@example.com'", cwd=main_repo_path)
    run_command("git config user.name 'Main User'", cwd=main_repo_path)

    # Create initial commit in main branch
    version_file = main_repo_path / "version.txt"
    version_file.write_text("01_01_0001")
    run_command("git add version.txt", cwd=main_repo_path)
    run_command("git commit -m 'Initial commit'", cwd=main_repo_path)

    # Create submodules
    submodules = {}
    for i in range(3):
        submodule_name = f"submodule_{i + 1}"
        submodule_path = main_repo_path / submodule_name
        create_submodule(submodule_path)
        submodules[submodule_name] = submodule_path

    update_submodules(main_repo_path, submodules)

    for itr in range(10):
        # Create branches and commits in submodules
        for name, sub_path in submodules.items():
            for j in range(3):  # Create 3 branches per submodule
                branch_name = f"branch_{j + 1}"

                run_command(f"git switch {branch_name} || git checkout -b {branch_name}", cwd=main_repo_path)
                create_commits(main_repo_path, branch_name, num_commits=2)
                run_command(f"git switch {branch_name} || git checkout -b {branch_name}", cwd=sub_path)
                create_commits(sub_path, branch_name, num_commits=10)
                run_command("git add .", cwd=main_repo_path)
                run_command(f"git commit -m 'Update submodule {submodule_name}'", cwd=main_repo_path)
                create_commits(main_repo_path, branch_name, num_commits=3)
                update_version_commit(main_repo_path, branch_name)

    print("\nRepository creation completed!")
    print(run_command("git branch", cwd=main_repo_path).stdout)
    print(run_command("git log --oneline -n 10", cwd=main_repo_path).stdout)


if __name__ == "__main__":
    create_test_repo()
