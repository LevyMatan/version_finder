// version_finder.js

const gitP = require('simple-git');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
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
    async init() {
        try {
            await this.git.checkIsRepo()
                .then(isRepo => {
                    if (!isRepo) {
                        throw new Error('Not a git repository');
                    }
                });
        } catch (error) {
            console.error(`Invalid git repository path: ${this.repositoryPath}`);
            return error;
        }

        try {
            const submodules_raw = await this.git.subModule(['status']);
            if (submodules_raw) {
                console.log("submodules_raw: ", submodules_raw);
                // Get submodule names:
                // THe submodules raw output looks like this:
                // <SHA> <SubModule Name> <submodule-branch>
                // Since we are only interested in the submodule name, we split the string by space and get the second element.
                // I need a way to remove empty string after the last '\n' character
                // I will use the split method to split the string by '\n' and then split each line by space to get the submodule name.
                // I will then remove the last element of the array since it is an empty string.
                // I will then assign the array to the submodules property.
                const submodules_raw_lines = submodules_raw.split('\n');
                console.log("submodules_raw_lines: ", submodules_raw_lines);
                // Remove the last element of the array if it is an empty string
                if (submodules_raw_lines[submodules_raw_lines.length - 1] === '') {
                    submodules_raw_lines.pop();
                }
                console.log("submodules_raw_lines: ", submodules_raw_lines);
                this.submodules = submodules_raw_lines.map(line => line.split(' ')[2]);
                console.log("submodules: ", this.submodules);
            } else {
                this.submodules = ['No submodules in Repo'];
            }
        } catch (error) {
            console.error('Error fetching submodule information.');
            this.submodules = ['No submodules in Repo'];
        }

        try {
            let branches = await this.git.branch();
            this.branches = branches.all.map(branch => branch.replace('origin/', '').replace('remotes/', ''));
            // Remove duplicates
            this.branches = [...new Set(this.branches)];
        } catch (error) {
            console.error('Error fetching branch information.');
            throw new Error('Error fetching branch information.');
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
            await this.git.subModule(['update', '--init']);
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
        console.log('checkAncestor: Command to be executed:', command_string);
        const { stdout, stderr } = await execPromise(command_string);
        console.log('Command executed . . .');
        console.log('stdout:', stdout);
        if (stderr) {
          isAncestor = false;
          console.error('stderr:', stderr);
        }
      } catch (error) {
        console.error(`exec error: ${error}`);
        console.error('return code:', error.code);
        isAncestor = false;
      }
      // Place the code that should execute after `exec` here
      console.log('Is ancestor:', isAncestor);
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
            console.log("In getFirstCommitSha: target_commit_hash: target_commit_hash= ",target_commit_hash, "branch=", branch, " submodule=", submodule);
            await this.git.checkout(branch);
            await this.git.pull();
            await this.git.subModule(['update', '--init']);
            if (submodule) {
                // Get the list of all commits that modified the submodule pointer
                let logs = await this.git.log({file: submodule});
                console.log("logs: ", logs);
                // Find the first commit that includes the target commit
                // Itertate over logs in reverse order to find the first commit that includes the target commit

                for (const log of logs.all.reverse()) {
                    // Check if the target_commit_hash is the ancestor of the current commit
                    console.log("log.hash: ", log.hash);
                    const lsTreeOutput = await this.git.raw(['ls-tree', log.hash, submodule]);
                    const match = lsTreeOutput.match(/\b[0-9a-f]{40}\b/); // Regex to match SHA-1 hash
                    const submodulePointer = match
                    const submoduleGit = gitP(path.join(this.repositoryPath, submodule));
                    console.log(`Git command to be executed: git merge-base --is-ancestor ${target_commit_hash} ${submodulePointer}`);
                    let isAncestor = true;
                    try {
                        // Check if the target commit is an ancestor of the submodule pointer
                        const submodulePath = path.join(this.repositoryPath, submodule);
                        // const mergeBase = await submoduleGit.raw(['merge-base', target_commit_hash, submodulePointer]);
                        // If the command does not throw, the exit status is 0, meaning the target_commit_hash is an ancestor.
                        isAncestor = await this.checkAncestor(submodulePath, target_commit_hash, submodulePointer);
                    } catch (error) {
                        // If the command throws, the exit status is non-zero.
                        // You can check error.message or error.stack for more details if needed.
                        // For 'git merge-base --is-ancestor', a non-zero exit status typically means the target_commit_hash is not an ancestor.
                        // However, it's good to check the specific error to distinguish between different non-zero exit statuses.
                        console.error('Error checking if commit is an ancestor:', error);
                        if (error.message.includes('is not an ancestor')) {
                            isAncestor = false;
                        } else {
                            // Handle other errors, possibly rethrow or log them.
                            console.error('Error checking if commit is an ancestor:', error);
                            throw error; // Rethrow if you want to escalate the error, or handle it as appropriate.
                        }
                    }
                    console.log('Is Ancestor:', isAncestor);

                    if (isAncestor) {
                        return log;
                    }
                }
                return null;
            } else {
                try {
                    let commitDetails = await this.git.raw(['show', '--no-patch', '--format={ "hash": "%H", "message": "%s"}', target_commit_hash]);
                    console.log("Commit Details: ", commitDetails);
                    commitDetails = JSON.parse(commitDetails);
                    return commitDetails
                } catch (error) {
                    console.error('Error fetching commit details for hash:', target_commit_hash);
                    console.error(error);
                }
            }
        } catch (error) {
            console.error('Error fetching first commit SHA.');
            console.error(error);
            return null;
        }
    }

    /**
     * Gets the logs for a given branch and submodule.
     * @param {string} branch - The branch name.
     * @param {string} submodule - The submodule name. Optional.
     * @returns {Promise<Object[]>} - A promise that resolves to an array of log objects.
     */
    async getLogs(branch, submodule=null, commit_hash='HEAD') {
        try {
            console.log("branch: ", branch);
            console.log("submodule: ", submodule);
            await this.git.checkout(branch);
            // await this.git.pull();
            await this.git.subModule(['update', '--init']);
            let logs;
            let gitRepo = this.git;
            if (submodule) {
                gitRepo = gitP(path.join(this.repositoryPath, submodule));
            }
            logs = await gitRepo.log({from: commit_hash});
            // Append the commit_hash to the logs
            const commit_hash_log = await gitRepo.raw(['show', '--no-patch', '--format={ "hash": "%H", "message": "%s"}', commit_hash]);
            console.log("commit_hash_log: ", commit_hash_log);
            logs.all.push(JSON.parse(commit_hash_log))
            return logs.all;
        } catch (error) {
            console.error('Error fetching logs.');
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
            console.error('Error fetching first commit with version.');
            return new Error('Error fetching first commit with version.');
        }
    }
}

module.exports = VersionFinder;
