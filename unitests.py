import unittest
from version_finder import VersionFinder

REPO_PATH = "/workspaces/version_finder"

class TestVersionFinder(unittest.TestCase):

    def setUp(self):
        self.vf = VersionFinder(REPO_PATH)

    def test_init(self):
        self.assertIsNotNone(self.vf)

    def test_get_submodules(self):
        submodules = self.vf.get_submodules()
        self.assertIsInstance(submodules, list)

    def test_get_branches(self):
        branches = self.vf.get_branches()
        self.assertIsInstance(branches, list)

    def test_is_valid_branch(self):
        branches = self.vf.get_branches()
        if branches:
            self.assertTrue(self.vf.is_valid_branch(branches[0]))
            self.assertFalse(self.vf.is_valid_branch("invalid_branch"))

    def test_is_valid_submodule(self):
        submodules = self.vf.get_submodules()
        if submodules:
            self.assertTrue(self.vf.is_valid_submodule(submodules[0]))
            self.assertFalse(self.vf.is_valid_submodule("invalid_submodule"))

    def test_is_valid_commit_sha(self):
        branches = self.vf.get_branches()
        if branches:
            self.assertTrue(self.vf.is_valid_commit_sha("HEAD", branches[0]))
            self.assertFalse(self.vf.is_valid_commit_sha("invalid_sha", branches[0]))

    def test_get_sha_of_first_commit_including_target(self):
        branches = self.vf.get_branches()
        if branches:
            sha = self.vf.get_sha_of_first_commit_including_target("HEAD", branches[0])
            self.assertIsNotNone(sha)

    def test_get_all_logs_until_commit(self):
        branches = self.vf.get_branches()
        if branches:
            logs = self.vf.get_all_logs_until_commit("HEAD", branches[0])
            self.assertIsNotNone(logs)

    def test_find_first_commit_with_version(self):
        branches = self.vf.get_branches()
        if branches:
            commit = self.vf.find_first_commit_with_version("HEAD", branches[0])
            self.assertIsNone(commit)

if __name__ == "__main__":
    unittest.main()
