// version_finder.js

const gitP = require('simple-git');
const path = require('path');

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
                this.submodules = (await this.git.subModule(['status'])).split('\n').map(line => line.split(' ')[1]);
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

    /**
     * Gets the first commit SHA for a given branch and submodule.
     * @param {string} branch - The branch name.
     * @param {string} submodule - The submodule name. Optional.
     * @returns {Promise<string>} - A promise that resolves to the first commit SHA.
     */
    async getFirstCommitSha(branch, submodule) {
        try {
            await this.git.checkout(branch);
            await this.git.pull();
            await this.git.subModule(['update', '--init']);
            let log;
            if (submodule) {
                log = await gitP(path.join(this.repositoryPath, submodule)).log();
            } else {
                log = await this.git.log();
            }
            return log.latest.hash;
        } catch (error) {
            console.error('Error fetching first commit SHA.');
            process.exit(1);
        }
    }

    /**
     * Gets the logs for a given branch and submodule.
     * @param {string} branch - The branch name.
     * @param {string} submodule - The submodule name. Optional.
     * @returns {Promise<Object[]>} - A promise that resolves to an array of log objects.
     */
    async getLogs(branch, submodule) {
        try {
            console.log("branch: ", branch);
            console.log("submodule: ", submodule);
            await this.git.checkout(branch);
            // await this.git.pull();
            await this.git.subModule(['update', '--init']);
            let logs;
            if (submodule) {
                logs = await gitP(path.join(this.repositoryPath, submodule)).log();
            } else {
                logs = await this.git.log();
            }
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
            const logs = await this.getLogs(branch, submodule);
            for (const log of logs) {
                if (log.message.includes("version")) {
                    return log.hash;
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
// ... rest of the script