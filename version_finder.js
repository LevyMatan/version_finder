// version_finder.js

const gitP = require('simple-git');
const path = require('path');

class VersionFinder {
    constructor(repositoryPath = process.cwd()) {
        this.repositoryPath = path.resolve(repositoryPath);
        this.git = gitP(this.repositoryPath);
        this.submodules = [];
        this.branches = [];
    }

    async init() {
        try {
            await this.git.checkIsRepo()
            .then(isRepo => {
                if (!isRepo) {
                    throw new Error('Not a git repository');
                }
            }
            )

        } catch (error) {
            console.error(`Invalid git repository path: ${this.repositoryPath}`);
            return error;
        }

        try {
            const submodules_raw = await this.git.subModule(['status']);
            if (submodules_raw) {
                console.log("submodules_raw: ", submodules_raw)
                this.submodules = (await this.git.subModule(['status'])).split('\n').map(line => line.split(' ')[1]);
            }
            else {
                this.submodules = ['No submodules in Repo'];
            }
        } catch (error) {
            console.error('Error fetching submodule information.');
            this.submodules = ['No submodules in Repo'];
        }

        try {
            let branches = await this.git.branch();
            this.branches = branches.all.map(branch => branch.replace('origin/', '').replace('remotes/', ''));
        } catch (error) {
            console.error('Error fetching branch information.');
            throw new Error('Error fetching branch information.');
        }
    }

    getSubmodules() {
        return this.submodules;
    }

    getBranches() {
        return this.branches;
    }

    isValidBranch(branch) {
        return this.branches.includes(branch);
    }

    isValidSubmodule(submodule) {
        return this.submodules.includes(submodule);
    }

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
            console.error(error)
            return error;
        }
    }

    async getFirstCommitWithVersion(commitSHA, branch, submodule) {
        try {
            const logs = await this.getLogs(branch, submodule);
            for (const log of logs) {
                if (log.message.includes("version")) {
                    return log.hash;
                }
            }
            return null;
        }
        catch (error) {
            console.error(error)
            console.error('Error fetching first commit with version.');
            return new Error('Error fetching first commit with version.');
        }
}}

module.exports = VersionFinder;
// ... rest of the script