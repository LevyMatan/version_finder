# version_finder.py

import subprocess
import sys
import os

class VersionFinder:

    def __init__(self, path=None) -> None:
        # Set CWD to the repository path
        if not path:
            self.repository_path = os.getcwd()
        else:
            self.repository_path = os.path.abspath(path)

        # Make sure the path is a valid git repository
        try:
            subprocess.check_output(["git", "rev-parse"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"Invalid git repository path: {self.repository_path}")
            sys.exit(1)

        if not self.__is_clean_git_repo():
            print("The repository is not clean. Please commit or stash your changes.")
            sys.exit(1)
        # Get a list of submodules in the main project
        try:
            output = subprocess.check_output(["git", "submodule", "status"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            self.submodules = [line.split()[1] for line in output.decode("utf-8").splitlines()]
        except subprocess.CalledProcessError:
            print("Error fetching submodule information.")
            sys.exit(1)

        # Get a list of all branches in the main project
        try:
            output = subprocess.check_output(["git", "branch", "-r"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            self.branches = [line.strip() for line in output.decode("utf-8").splitlines()]
            # Remove the `HEAD -> <current_branch>` branch
            self.branches = self.branches[1:]
            # Remove the origin/ prefix
            self.branches = [branch.split("/", 1)[1] for branch in self.branches]
        except subprocess.CalledProcessError:
            print("Error fetching branch information.")
            sys.exit(1)

    def get_submodules(self):
        return self.submodules

    def get_branches(self):
        return self.branches

    def is_valid_branch(self, branch):
        return branch in self.branches
    
    def is_valid_submodule(self, submodule):
        return submodule in self.submodules
    
    def is_valid_commit_sha(self, commit_sha, branch, submodule=None):
        try:
            # Checkout the branch
            subprocess.check_output(["git", "checkout", branch], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            # Pull
            subprocess.check_output(["git", "pull"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            # Update sumodules
            subprocess.check_output(["git", "submodule", "update", "--init"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            if submodule:
                # Go to the submodule directory
                path = os.path.join(self.repository_path, submodule)
            else:
                path = self.repository_path

            # Verify the commit exists in the submodule
            subprocess.check_output(["git", "show", commit_sha], cwd=path, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
        
    def __is_clean_git_repo(self):
        '''
        Check if the repository is clean.
        '''
        try:
            subprocess.check_output(["git", "diff", "--quiet"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
    

    def __is_ancestor(self, ancestor, commit, submodule=None):
        '''
        Check if the commit is an ancestor of the ancestor commit.

        Note: Assumes the two commits exists in the repository/submodule, and that we are the root of the repository/submodule.
        '''
        if submodule:
            path = os.path.join(self.repository_path, submodule)
        else:
            path = self.repository_path
        try:
            subprocess.check_output(["git", "merge-base", "--is-ancestor",ancestor, commit], cwd=path, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
        
    def __get_pointer_to_submodule(self, submodule, branch=""):
        try:
            if branch:
                # Checkout the branch
                subprocess.check_output(["git", "checkout", branch], cwd=self.repository_path, stderr=subprocess.DEVNULL)
                # Update sumodules
                subprocess.check_output(["git", "submodule", "update", "--init"], cwd=self.repository_path, stderr=subprocess.DEVNULL)

            # Get the commit SHA of the repository/submodule in the branch
            if submodule:
                output = subprocess.check_output(["git", "submodule", "status", submodule], cwd=self.repository_path, stderr=subprocess.DEVNULL)
                return output.decode("utf-8").split()[0]
            else:
                output = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
                return output.decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return None

    def __get_submodule_pointer_at_specific_repo_commit(self, submodule, commit):
        try:
            output = subprocess.check_output(["git", "ls-tree", commit, submodule], cwd=self.repository_path, stderr=subprocess.DEVNULL)  
            return output.decode("utf-8").split()[2]
        except subprocess.CalledProcessError:
            return None  
        
    def get_sha_of_first_commit_including_target(self, target, branch, submodule=None):
        try:
            # Checkout the branch
            subprocess.check_output(["git", "checkout", branch], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            # Update sumodules
            subprocess.check_output(["git", "submodule", "update", "--init"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            if submodule:
                # Iterate over all commits in repository that changed the submodule
                output = subprocess.check_output(["git", "rev-list", "HEAD", "--", submodule], cwd=self.repository_path, stderr=subprocess.DEVNULL)
                commits_list = output.decode("utf-8").splitlines()
                for indx,commit in enumerate(commits_list):
                    submodule_commit = self.__get_submodule_pointer_at_specific_repo_commit(submodule, commit)
                    if not self.__is_ancestor(target, submodule_commit, submodule=submodule):
                        return commits_list[indx-1]
            else:
                return target
        except subprocess.CalledProcessError:
            return None
        
    def get_all_logs_until_commit(self, commit, branch, submodule=None):
        try:
            # Checkout the branch
            subprocess.check_output(["git", "checkout", branch], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            # Update sumodules
            subprocess.check_output(["git", "submodule", "update", "--init"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            if submodule:
                path = os.path.join(self.repository_path, submodule)
            else:
                path = self.repository_path
            # Show all logs until the commit
            output = subprocess.check_output(["git", "log", f"{commit}..HEAD", "--oneline", "--reverse"], cwd=self.repository_path, stderr=subprocess.DEVNULL)
            return (output.decode("utf-8"))
        except subprocess.CalledProcessError:
            print("Error showing logs.")
            sys.exit(1)

    def find_first_commit_with_version(self, commit, branch, submodule=None):
        gitlog = self.get_all_logs_until_commit(commit, branch, submodule)
        for line in gitlog.splitlines():
            if "Version:" in line:
                print ("The first version including the commit is:")
                print (line)
                return line.split()[0]
        print ("No version found in the logs.")


if __name__ == "__main__":

    # Get the path of the repository from the command line invoke as argument
    if len(sys.argv) != 2:
        print("Usage: python version_finder.py [path_to_repository=.]")
        print("Setting repository path to the current directory.")
        path = None
    else:
        path = sys.argv[1]

    version_finder = VersionFinder(path)
    submodules = version_finder.get_submodules()
    branches = version_finder.get_branches()

    # Set default values
    selected_submodule = None
    selected_branch = "main"

    if submodules:
        print("Available submodules:")
        for submodule in submodules:
            print(f"- {submodule}")

        selected_submodule = input("Enter the submodule path (e.g., sub-module-A): ")
        # Verify the selected submodule
        if not version_finder.is_valid_submodule(selected_submodule):
            print("Invalid submodule path.")
            sys.exit(1)
    else:
        print("No submodules found.")

    print("\nAvailable branches:")
    for branch in branches:
        print(f"- {branch}")

    selected_branch = input("\nEnter the branch name: ")
    # Verify the selected branch
    if not version_finder.is_valid_branch(selected_branch):
        print("Invalid branch name.")
        sys.exit(1)

    selected_sha = input("Enter the commit SHA: ")

    if not version_finder.is_valid_commit_sha(selected_sha, selected_branch, selected_submodule):
        print("Invalid commit SHA.")
        sys.exit(1)

    first_commit_sha = version_finder.get_sha_of_first_commit_including_target(selected_sha, selected_branch, selected_submodule)
    print(f"The SHA of the first commit including the target is: {first_commit_sha}")

    print("\nLogs until the first commit including the target: (From Head to the first commit including the target)")
    print(version_finder.get_all_logs_until_commit(first_commit_sha, selected_branch, selected_submodule))

    version_finder.find_first_commit_with_version(first_commit_sha, selected_branch, selected_submodule)