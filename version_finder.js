// version_finder.js

const gitP = require("simple-git");
const path = require("path");
const { exec } = require("child_process");
const util = require("util");
const execPromise = util.promisify(exec);

/**
 * Represents a VersionFinder object that provides methods to interact with a git repository.
 */
class VersionFinder {
  /**
   * Creates a new VersionFinder object.
   * @param {string} repositoryPath - The path to the git repository. Defaults to the current working directory.
   */
  constructor(repositoryPath = process.cwd()) {
    this.repositoryPath = path.resolve(repositoryPath);
    this.git = gitP(this.repositoryPath);
    this.submodules = [];
    this.branches = [];
  }

  /**
   * Initializes the VersionFinder object by checking if the repository is valid and fetching submodule and branch information.
   * @returns {Promise<Error|null>} - A promise that resolves to null if initialization is successful, or an Error object if there is an error.
   */
  /**
   * Initializes the version finder by checking if the current directory is a git repository,
   * fetching submodule information, and fetching branch information.
   * @returns {Promise<Error>} An error object if any error occurs during initialization.
   */
  async init() {
    try {
      await this.git.checkIsRepo().then((isRepo) => {
        if (!isRepo) {
          throw new Error("Not a git repository");
        }
      });
    } catch (error) {
      console.error(`Invalid git repository path: ${this.repositoryPath}`);
      throw error;
    }

    try {
      const submodules_raw = await this.git.subModule(["status"]);
      if (submodules_raw) {
        const submodules_raw_lines = submodules_raw.split("\n");
        if (submodules_raw_lines[submodules_raw_lines.length - 1] === "") {
          submodules_raw_lines.pop();
        }
        this.submodules = submodules_raw_lines.map(
          (line) => line.split(" ")[2]
        );
      } else {
        this.submodules = ["No submodules in Repo"];
      }
    } catch (error) {
      console.error("Error fetching submodule information.");
      this.submodules = ["No submodules in Repo"];
    }

    try {
      let branches = await this.git.branch();
      this.branches = branches.all.map((branch) =>
        branch.replace("origin/", "").replace("remotes/", "")
      );
      // Remove duplicates
      this.branches = [...new Set(this.branches)];
    } catch (error) {
      console.error("Error fetching branch information.");
      throw new Error("Error fetching branch information.");
    }
  }

  /**
   * Gets the list of submodules in the repository.
   * @returns {string[]} - An array of submodule names.
   */
  getSubmodules() {
    return this.submodules;
  }

  /**
   * Gets the list of branches in the repository.
   * @returns {string[]} - An array of branch names.
   */
  getBranches() {
    return this.branches;
  }

  /**
   * Checks if a branch is valid.
   * @param {string} branch - The branch name to check.
   * @returns {boolean} - true if the branch is valid, false otherwise.
   */
  isValidBranch(branch) {
    return this.branches.includes(branch);
  }

  /**
   * Checks if a submodule is valid.
   * @param {string} submodule - The submodule name to check.
   * @returns {boolean} - true if the submodule is valid, false otherwise.
   */
  isValidSubmodule(submodule) {
    return this.submodules.includes(submodule);
  }

  /**
   * Checks if a commit SHA is valid for a given branch and submodule.
   * @param {string} commitSha - The commit SHA to check.
   * @param {string} branch - The branch name.
   * @param {string} submodule - The submodule name. Optional.
   * @returns {Promise<boolean>} - A promise that resolves to true if the commit SHA is valid, false otherwise.
   */
  async isValidCommitSha(commitSha, branch, submodule) {
    try {
      await this.git.checkout(branch);
      await this.git.pull();
      await this.git.subModule(["update", "--init"]);
      if (submodule) {
        await gitP(path.join(this.repositoryPath, submodule)).show([commitSha]);
      } else {
        await this.git.show([commitSha]);
      }
      return true;
    } catch (error) {
      return false;
    }
  }

  async checkAncestor(submodulePath, target_commit_hash, submodulePointer) {
    let isAncestor = true;
    try {
      const command_string = `cd ${submodulePath} && git merge-base --is-ancestor ${target_commit_hash} ${submodulePointer}`;
      const { stdout, stderr } = await execPromise(command_string);
      if (stderr) {
        isAncestor = false;
        console.error("stderr:", stderr);
      }
    } catch (error) {
      if ( 1 === error.code ) {
        isAncestor = false;
      } else {
        throw error;
      }
    }
    return isAncestor;
  }

  /**
   * Gets the first commit SHA for a given branch and submodule.
   * @param {string} branch - The branch name.
   * @param {string} submodule - The submodule name. Optional.
   * @returns {Promise<string>} - A promise that resolves to the first commit SHA.
   */
  async getFirstCommitSha(target_commit_hash, branch, submodule) {
    try {
      console.log(
        "In getFirstCommitSha: target_commit_hash=",
        target_commit_hash,
        "branch=",
        branch,
        "submodule=",
        submodule
      );
      await this.git.checkout(branch);
      await this.git.pull();
      await this.git.subModule(["update", "--init"]);
      if (submodule) {
        let logs = await this.git.log({
          file: submodule,
          format: { hash: "%H", message: "%s" },
        });
        // Convert logs to an array if not already
        logs = logs.all || [];

        // Binary search function
        const binarySearch = async (logs) => {
          let low = 0;
          let high = logs.length - 1;
          const submodulePath = path.join(this.repositoryPath, submodule);
          console.log("submodulePath: ", submodulePath);
          console.log("submodule: ", submodule);
          while (low <= high) {
            const mid = Math.floor((low + high) / 2);
            const log = logs[mid];
            const lsTreeOutput = await this.git.raw([
              "ls-tree",
              log.hash,
              submodule,
            ]);
            const match = lsTreeOutput.match(/\b[0-9a-f]{40}\b/);
            if (!match) continue; // Skip if no match found
            const submodulePointer = match[0];
            const isAncestor = await this.checkAncestor(
              submodulePath,
              target_commit_hash,
              submodulePointer
            );
            if (isAncestor) {
              // If isAncestor, search left (earlier commits)
              high = mid - 1;
            } else {
              // If not ancestor, search right (later commits)
              low = mid + 1;
            }
          }
          // Return the log at the boundary if it's an ancestor, else null
          if (low < logs.length) {
            const lsTreeOutput = await this.git.raw([
              "ls-tree",
              logs[low].hash,
              submodule,
            ]);
            const match = lsTreeOutput.match(/\b[0-9a-f]{40}\b/);
            if (match) {
              const submodulePointer = match[0];
              const isAncestor = await this.checkAncestor(
                submodulePath,
                target_commit_hash,
                submodulePointer
              );
              if (isAncestor) {
                return logs[low];
              }
            }
          }
          return null;
        };

        return await binarySearch(logs.reverse()); // Reverse logs to have them in chronological order for binary search
      } else {
        // Handle the case where there's no submodule
        let commitDetails = await this.git.raw([
          "show",
          "--no-patch",
          '--format={"hash": "%H", "message": "%s"}',
          target_commit_hash,
        ]);
        commitDetails = JSON.parse(commitDetails);
        return commitDetails;
      }
    } catch (error) {
      console.error("Error fetching first commit SHA.");
      console.error(error);
      throw error;
    }
  }

  /**
   * Gets the logs for a given branch and submodule.
   * @param {string} branch - The branch name.
   * @param {string} submodule - The submodule name. Optional.
   * @returns {Promise<Object[]>} - A promise that resolves to an array of log objects.
   */
  async getLogs(branch, submodule = null, commit_hash = "HEAD") {
    try {
      console.log("branch: ", branch);
      console.log("submodule: ", submodule);
      await this.git.checkout(branch);
      // await this.git.pull();
      await this.git.subModule(["update", "--init"]);
      let logs;
      let gitRepo = this.git;
      if (submodule) {
        gitRepo = gitP(path.join(this.repositoryPath, submodule));
      }
      logs = await gitRepo.log({ from: commit_hash });
      // Append the commit_hash to the logs
      const commit_hash_log = await gitRepo.raw([
        "show",
        "--no-patch",
        '--format={ "hash": "%H", "message": "%s"}',
        commit_hash,
      ]);
      logs.all.push(JSON.parse(commit_hash_log));
      return logs.all;
    } catch (error) {
      console.error("Error fetching logs.");
      console.error(error);
      return error;
    }
  }

  /**
   * Gets the first commit SHA that contains a version in the commit message for a given branch and submodule.
   * @param {string} commitSHA - The commit SHA to start searching from.
   * @param {string} branch - The branch name.
   * @param {string} submodule - The submodule name. Optional.
   * @returns {Promise<string|null>} - A promise that resolves to the first commit SHA that contains a version, or null if no such commit is found.
   */
  async getFirstCommitWithVersion(commitSHA, branch, submodule) {
    try {
      console.log("In getFirstCommitWithVersion");
      console.log("commitSHA: ", commitSHA);
      console.log("branch: ", branch);
      console.log("submodule: ", submodule);
      const logs = await this.getLogs(branch, null, commitSHA);
      console.log("logs: ", logs);
      for (const log of logs.reverse()) {
        if (log.message.match(/Version: (\d+\.\d+\.\d+)/)) {
          return log;
        }
      }
      return null;
    } catch (error) {
      console.error(error);
      console.error("Error fetching first commit with version.");
      return new Error("Error fetching first commit with version.");
    }
  }
}

module.exports = VersionFinder;
