# version_finder.py

import subprocess
import sys

class VersionFinder:

    def __init__(self) -> None:
        if not self.__is_clean_git_repo():
            print("The repository is not clean. Please commit or stash your changes.")
            sys.exit(1)
        # Get a list of submodules in the main project
        try:
            output = subprocess.check_output(["git", "submodule", "status"], stderr=subprocess.DEVNULL)
            self.submodules = [line.split()[1] for line in output.decode("utf-8").splitlines()]
        except subprocess.CalledProcessError:
            print("Error fetching submodule information.")
            sys.exit(1)

        # Get a list of all branches in the main project
        try:
            output = subprocess.check_output(["git", "branch", "-r"], stderr=subprocess.DEVNULL)
            self.branches = [line.strip() for line in output.decode("utf-8").splitlines()]
            # Remove the origin/ prefix
            self.branches = [branch.split("/", 1)[1] for branch in self.branches]
        except subprocess.CalledProcessError:
            print("Error fetching branch information.")
            sys.exit(1)

    def get_submodules(self):
        return self.submodules

    def get_branches(self):
        return self.branches

    def is_valid_commit_sha(self, commit_sha, branch, submodule):
        try:
            # Checkout the branch
            subprocess.check_output(["git", "checkout", branch], stderr=subprocess.DEVNULL)
            # Update sumodules
            subprocess.check_output(["git", "submodule", "update", "--init"], stderr=subprocess.DEVNULL)
            if submodule:
                # Go to the submodule directory
                subprocess.check_output(["cd", submodule], stderr=subprocess.DEVNULL)
            # Verify the commit exists in the submodule
            subprocess.check_output(["git", "show", commit_sha], stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
        
    def __is_clean_git_repo(self):
        try:
            subprocess.check_output(["git", "diff", "--quiet"], stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
    

    def __is_ancestor(self, ancestor, commit):
        '''
        Check if the commit is an ancestor of the ancestor commit.

        Note: Assumes the two commits exists in the repository/submodule, and that we are the root of the repository/submodule.
        '''
        try:
            subprocess.check_output(["git", "merge-base", "--is-ancestor",ancestor, commit], stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
        
    def __get_pointer_to_submodule(self, submodule, branch):
        try:
            # Checkout the branch
            subprocess.check_output(["git", "checkout", branch], stderr=subprocess.DEVNULL)
            # Update sumodules
            subprocess.check_output(["git", "submodule", "update", "--init"], stderr=subprocess.DEVNULL)
            # Get the commit SHA of the submodule in the branch
            output = subprocess.check_output(["git", "submodule", "status", submodule], stderr=subprocess.DEVNULL)
            return output.decode("utf-8").split()[0]
        except subprocess.CalledProcessError:
            return None
        
    def get_sha_of_first_commit_including_target(self, target, branch):
        try:
            # Checkout the branch
            subprocess.check_output(["git", "checkout", branch], stderr=subprocess.DEVNULL)
            # Update sumodules
            subprocess.check_output(["git", "submodule", "update", "--init"], stderr=subprocess.DEVNULL)
            # Checkout the branch
            subprocess.check_output(["git", "checkout", branch], stderr=subprocess.DEVNULL)
            # Get the commit SHA of the first commit including the target
            output = subprocess.check_output(["git", "rev-list", target, "--topo-order", "--reverse"], stderr=subprocess.DEVNULL)
            return output.decode("utf-8").splitlines()[-1]
        except subprocess.CalledProcessError:
            return None

if __name__ == "__main__":

    version_finder = VersionFinder()
    submodules = version_finder.get_submodules()
    branches = version_finder.get_branches()

    print("Available submodules:")
    for submodule in submodules:
        print(f"- {submodule}")

    print("\nAvailable branches:")
    for branch in branches:
        print(f"- {branch}")

    selected_branch = input("\nEnter the branch name: ")
    # Verify the selected branch
    if selected_branch not in branches:
        print("Invalid branch name.")
        sys.exit(1)
    
    if not submodules:
        print("No submodules found. Searching in main repository.")
        selected_submodule = ""
    else:
        selected_submodule = input("Enter the submodule path (e.g., sub-module-A): ")
        # Verify the selected submodule
        if selected_submodule not in submodules:
            print("Invalid submodule path.")
            sys.exit(1)

    selected_sha = input("Enter the commit SHA: ")

    if not version_finder.is_valid_commit_sha(selected_sha, selected_branch, selected_submodule):
        print("Invalid commit SHA.")
        sys.exit(1)