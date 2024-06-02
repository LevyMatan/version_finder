# version_finder.py

import subprocess
import sys

def get_submodules():
    # Get a list of submodules in the main project
    try:
        output = subprocess.check_output(["git", "submodule", "status"], stderr=subprocess.DEVNULL)
        submodules = [line.split()[1] for line in output.decode("utf-8").splitlines()]
        return submodules
    except subprocess.CalledProcessError:
        print("Error fetching submodule information.")
        sys.exit(1)

def get_branches():
    # Get a list of all branches in the main project
    try:
        output = subprocess.check_output(["git", "branch", "-a"], stderr=subprocess.DEVNULL)
        branches = [line.strip() for line in output.decode("utf-8").splitlines()]
        return branches
    except subprocess.CalledProcessError:
        print("Error fetching branch information.")
        sys.exit(1)

def find_version_for_submodule(submodule, branch, submodule_sha):
    # Checkout the specified branch
    subprocess.run(["git", "checkout", branch])

    # Get submodule's commit details
    try:
        output = subprocess.check_output(["git", "show", submodule_sha], stderr=subprocess.DEVNULL)
        submodule_commit = output.decode("utf-8")
    except subprocess.CalledProcessError:
        print(f"Error fetching commit details for {submodule_sha}.")
        sys.exit(1)

    # Traverse main project's commit history
    try:
        output = subprocess.check_output(["git", "log", "--oneline"], stderr=subprocess.DEVNULL)
        commits = [line.split()[0] for line in output.decode("utf-8").splitlines()]
        for commit in commits:
            if submodule_commit in commit:
                print(f"Submodule commit {submodule_sha} introduced in version: {commit}")
                break
        else:
            print(f"Submodule commit {submodule_sha} not found in any version.")
    except subprocess.CalledProcessError:
        print("Error fetching commit history.")
        sys.exit(1)

if __name__ == "__main__":
    submodules = get_submodules()
    branches = get_branches()

    print("Available submodules:")
    for submodule in submodules:
        print(f"- {submodule}")

    print("\nAvailable branches:")
    for branch in branches:
        print(f"- {branch}")

    selected_branch = input("\nEnter the branch name: ")
    selected_submodule = input("Enter the submodule path (e.g., sub-module-A): ")
    selected_sha = input("Enter the commit SHA: ")

    find_version_for_submodule(selected_submodule, selected_branch, selected_sha)
