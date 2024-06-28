// version_finder.js

const gitP = require("simple-git");
const path = require("path");
const { exec } = require("child_process");
const util = require("util");
const execPromise = util.promisify(exec);
const fs = require("fs");

/**
 * Represents a VersionFinder object that provides methods to interact with a git repository.
 */
/**
 * Represents a VersionFinder object that is used to find versions in a Git repository.
 */
class VersionFinder {
  /**
   * Creates a new VersionFinder object.
   * @param {string} repositoryPath - The path to the git repository. Defaults to the current working directory.
   */
  constructor(repositoryPath = process.cwd()) {
    this.repositoryPath = path.resolve(repositoryPath);

    if (!fs.existsSync(this.repositoryPath)) {
      console.error(
        `The provided path "${this.repositoryPath}" does not exist.`
      );
      // Handle the error appropriately. For example, you might want to throw an error or set an internal state.
      throw new Error(
        `The provided path "${this.repositoryPath}" does not exist.`
      );
    }
    this.git = gitP(this.repositoryPath);
    this.submodules = [];
    this.branches = [];
    this.searchPatternRegex = null;
    this.isInitialized = false;
    this.hasChanges = false;
    this.snapshot = null;
  }

  async destructor() {
    console.log("In destructor");
    await this.restoreRepoSnapshot();
    this.repositoryPath = null;
    this.git = null;
    this.submodules = null;
    this.branches = null;
    this.searchPatternRegex = null;
    this.isInitialized = null;
    this.hasChanges = null;
  }

  /**
   * Sets the search pattern for the version finder.
   * @param {string} searchPattern - The search pattern to set.
   * @throws {Error} If the search pattern is not a string or is not a valid regex.
   */
  setSearchPattern(searchPattern) {
    // Validate the input is a string and not a regex
    if (typeof searchPattern !== "string") {
      throw new Error("The search pattern must be a string.");
    }

    // Validate the string is a valid regex
    if (
      !searchPattern.startsWith("/") ||
      searchPattern.lastIndexOf("/") === 0
    ) {
      throw new Error("The search pattern must be a valid regex.");
    }

    console.log("searchPattern: ", searchPattern);
    const regexBody = searchPattern.slice(1, searchPattern.lastIndexOf("/"));

    // Extract flags if present
    const regexFlags = searchPattern.slice(searchPattern.lastIndexOf("/") + 1);

    this.searchPatternRegex = new RegExp(regexBody, regexFlags);
    console.log("searchPatternRegex: ", this.searchPatternRegex);
  }

  /**
   * Checks if a Git repository is dirty (has uncommitted changes).
   * @param {SimpleGit} gitRepo - The SimpleGit instance representing the Git repository.
   * @returns {Promise<boolean>} - A Promise that resolves to `true` if the repository is dirty, or `false` otherwise.
   */
  async isRepoDirty(gitRepo) {
    const status = await gitRepo.status(["-uno"]);
    let isDirty = false;
    if (status.files.length > 0) {
      console.warn(
        "Warning: The repository has uncommitted changes. This may affect the results."
      );
      isDirty = true;
    }
    return isDirty;
  }

  /**
   * Initializes the VersionFinder object by checking if the repository is valid and fetching submodule and branch information.
   * @returns {Promise<Error|null>} - A promise that resolves to null if initialization is successful, or an Error object if there is an error.
   */
  async init() {
    if (this.isInitialized) {
      return;
    }
    await this.git.checkIsRepo().then((isRepo) => {
      if (!isRepo) {
        throw new Error(
          `The given path ${this.repositoryPath} is Not a git repository`
        );
      }
    });

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
        this.submodules = [];
      }
    } catch (e) {
      console.error("Error fetching submodule information.");
      this.submodules = [];
      throw e;
    }

    try {
      let branches = await this.git.branch();
      this.branches = branches.all.map((branch) =>
        branch.replace("origin/", "").replace("remotes/", "")
      );
      // Remove duplicates
      this.branches = [...new Set(this.branches)];
    } catch (e) {
      console.error("Error fetching branch information.");
      throw e;
    }

    // Check if repository is "clean" (no uncommitted changes)
    this.hasChanges = await this.isRepoDirty(this.git);

    // Save the repo status
    await this.saveRepoSnapshot(false);

    // Set the initialized flag
    this.isInitialized = true;
  }

  /**
   * Gets the list of submodules in the repository.
   * @returns {string[]} - An array of submodule names.
   */
  getSubmodules() {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    return this.submodules;
  }

  /**
   * Gets the list of branches in the repository.
   * @returns {string[]} - An array of branch names.
   */
  getBranches() {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    return this.branches;
  }

  /**
   * Checks if a branch is valid.
   * @param {string} branch - The branch name to check.
   * @returns {boolean} - true if the branch is valid, false otherwise.
   */
  isValidBranch(branch) {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    return this.branches.includes(branch);
  }

  /**
   * Checks if a submodule is valid.
   * @param {string} submodule - The submodule name to check.
   * @returns {boolean} - true if the submodule is valid, false otherwise.
   */
  isValidSubmodule(submodule) {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    return this.submodules.includes(submodule);
  }

  /**
   * Takes a snapshot of the given git repository.
   *
   * @param {GitRepo} gitRepo - The git repository object.
   * @returns {Promise<Object>} A promise that resolves to an object containing the snapshot information.
   */
  async takeRepoSnapshot(gitRepo, allow_to_stash = true) {
    const snapshot = {
      commitHash: null,
      branch: null,
      stashId: null,
    };
    if ((await this.isRepoDirty(gitRepo)) && allow_to_stash) {
      // Stash the changes
      const stash = await gitRepo.stash(["save", "VersionFinder snapshot"]);
      console.log("stash: ", stash);
      // Get the id by fetching the list of stashes
      const stashList = await gitRepo.stash(["list"]);
      for (const stashEntry of stashList.split("\n")) {
        console.log("stashEntry: ", stashEntry);
        if (stashEntry.includes("VersionFinder snapshot")) {
          snapshot.stashId = stashEntry.match(/stash@\{0\}/)[0];
          break;
        }
      }
    } else {
      snapshot.stashId = null;
    }
    let branch = await gitRepo.revparse(["--abbrev-ref", "HEAD"]);
    if (branch === "HEAD") {
      branch = null;
    }
    const commitHash = await gitRepo.revparse(["HEAD"]);
    snapshot.commitHash = commitHash;
    snapshot.branch = branch;

    return snapshot;
  }

  /**
   * Saves the current state of the repository to a snapshot.
   *
   * @throws {Error} If VersionFinder is not initialized.
   */
  async saveRepoSnapshot(allow_to_stash = true) {
    console.log("In saveRepoSnapshot");
    if (this.snapshot && this.snapshot.isAllowedToStash === true) {
      console.log("In saveRepoSnapshot: snapshot already exists");
      return;
    }

    // Create a snapshot object
    const snapshot = {
      isAllowedToStash: allow_to_stash,
      mainRepo: {
        commitHash: "",
        branch: "",
        stashId: "",
      },
      submodules: {},
    };

    // Iterate over all submodules
    console.log("this.submodules: ", this.submodules);
    for (const submodule of this.submodules) {
      const submodulePath = path.join(this.repositoryPath, submodule);
      console.log("submodulePath: ", submodulePath);
      const gitSubmoduleRepo = gitP(submodulePath);
      snapshot.submodules[submodule] = await this.takeRepoSnapshot(
        gitSubmoduleRepo,
        allow_to_stash
      );
    }

    // Save the state of the main repository
    snapshot.mainRepo = await this.takeRepoSnapshot(this.git, allow_to_stash);

    // Save the snapshot to this.snapshot
    this.snapshot = snapshot;
    this.hasChanges = this.isRepoDirty(this.git);

    console.log("snapshot: ", snapshot);
  }

  /**
   * Undoes a repository snapshot by checking out the branch or commit hash and restoring the stash if applicable.
   * @param {GitRepo} gitRepo - The Git repository object.
   * @param {Object} snapshot - The snapshot object containing information about the snapshot.
   * @param {string} [snapshot.branch] - The branch to check out.
   * @param {string} [snapshot.commitHash] - The commit hash to check out.
   * @param {string} [snapshot.stashId] - The stash ID to restore.
   * @returns {Promise<void>} - A promise that resolves when the snapshot is undone.
   */
  async undoRepoSnapshot(gitRepo, snapshot) {
    console.log("In undoRepoSnapshot");
    if (snapshot.branch) {
      await gitRepo.checkout(snapshot.branch);
    } else {
      await gitRepo.checkout(snapshot.commitHash);
    }
    if (snapshot.stashId) {
      // Restore the stash
      await gitRepo.stash(["pop", snapshot.stashId]);
    }
  }

  /**
   * Restores the repository to the state saved in the snapshot.
   * Iterates over all submodules and restores the commit hash and branch name if they exist.
   * If a submodule had uncommitted changes, restores the stash.
   * Does the same for the main repository.
   * @throws {Error} If VersionFinder is not initialized.
   */
  async restoreRepoSnapshot() {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    console.log("In restoreRepoSnapshot");
    if (this.snapshot) {
      console.log("In restoreRepoSnapshot: snapshot");
      console.log("snapshot: ", this.snapshot);
      /**
       * Restore the repository to the state saved in the snapshot.
       * Iterate over all submodules and restore the commit hash and branch name if exists.
       * If a submodule had uncommited changes, restore the stash.
       * Do the same for the main repository.
       */
      const snapshot = this.snapshot;

      // Iterate over all submodules
      for (const submodule of this.submodules) {
        const submodulePath = path.join(this.repositoryPath, submodule);
        const gitRepo = gitP(submodulePath);
        const submoduleSnapshot = snapshot.submodules[submodule];
        await this.undoRepoSnapshot(gitRepo, submoduleSnapshot);
      }

      // Restore the state of the main repository
      const mainRepoSnapshot = snapshot.mainRepo;
      await this.undoRepoSnapshot(this.git, mainRepoSnapshot);

      // Clear the snapshot
      this.snapshot = null;
      this.hasChanges = true;
    }
  }

  /**
   * Checks if a commit SHA is valid for a given branch and submodule.
   * @param {string} commitSha - The commit SHA to check.
   * @param {string} branch - The branch name.
   * @param {string} submodule - The submodule name. Optional.
   * @returns {Promise<boolean>} - A promise that resolves to true if the commit SHA is valid, false otherwise.
   */
  async isValidCommitSha(commitSha, branch, submodule) {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    if (this.hasChanges) {
      throw new Error(
        "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
      );
    }
    await this.saveRepoSnapshot();
    await this.git.checkout(branch);
    await this.git.pull();
    await this.git.subModule(["update", "--init"]);
    if (submodule) {
      await gitP(path.join(this.repositoryPath, submodule)).show([commitSha]);
    } else {
      await this.git.show([commitSha]);
    }
    await this.restoreRepoSnapshot();
    return true;
  }

  /**
   * Checks if a submodule is an ancestor of a target commit hash.
   *
   * @param {string} submodulePath - The path to the submodule.
   * @param {string} target_commit_hash - The target commit hash.
   * @param {string} submodulePointer - The submodule pointer.
   * @returns {boolean} - Returns true if the submodule is an ancestor, false otherwise.
   * @throws {Error} - Throws an error if VersionFinder is not initialized.
   */
  async checkAncestor(submodulePath, target_commit_hash, submodulePointer) {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    let isAncestor = true;
    try {
      const command_string = `cd ${submodulePath} && git merge-base --is-ancestor ${target_commit_hash} ${submodulePointer}`;
      const { stderr } = await execPromise(command_string);
      if (stderr) {
        isAncestor = false;
        console.error("stderr:", stderr);
      }
    } catch (error) {
      if (1 === error.code) {
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
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    if (this.hasChanges) {
      throw new Error(
        "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
      );
    }
    try {
      await this.saveRepoSnapshot();
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
    } finally {
      await this.restoreRepoSnapshot();
    }
  }

  /**
   * Gets the logs for a given branch and submodule.
   * @param {string} branch - The branch name.
   * @param {string} submodule - The submodule name. Optional.
   * @returns {Promise<Object[]>} - A promise that resolves to an array of log objects.
   */
  async getLogs(branch, submodule = null, commit_hash = "HEAD") {
    if (!this.isInitialized) {
      throw new Error("VersionFinder is not initialized.");
    }
    if (this.hasChanges) {
      throw new Error(
        "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
      );
    }
    try {
      await this.saveRepoSnapshot();
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
      throw error;
    } finally {
      await this.restoreRepoSnapshot();
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
    console.log("In getFirstCommitWithVersion");
    console.log("commitSHA: ", commitSHA);
    console.log("branch: ", branch);
    console.log("submodule: ", submodule);
    if (this.hasChanges) {
      throw new Error(
        "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
      );
    }
    try {
      const logs = await this.getLogs(branch, null, commitSHA);
      console.log("logs: ", logs);
      for (const log of logs.reverse()) {
        if (log.message.match(this.searchPatternRegex)) {
          return log;
        }
      }
      return null;
    } catch (error) {
      console.error(error);
      console.error("Error fetching first commit with version.");
      throw error;
    }
  }
}

module.exports = { VersionFinder };
