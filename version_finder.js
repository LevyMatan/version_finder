// version_finder.js

const gitP = require('simple-git/promise');
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
            await this.git.checkIsRepo();
        } catch (error) {
            console.error(`Invalid git repository path: ${this.repositoryPath}`);
            process.exit(1);
        }

        try {
            this.submodules = (await this.git.subModule(['status'])).split('\n').map(line => line.split(' ')[1]);
        } catch (error) {
            console.error('Error fetching submodule information.');
            process.exit(1);
        }

        try {
            this.branches = (await this.git.branch(['-r'])).all.map(branch => branch.split('/', 2)[1]);
        } catch (error) {
            console.error('Error fetching branch information.');
            process.exit(1);
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
            await this.git.checkout(branch);
            await this.git.pull();
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
            process.exit(1);
        }
    }

    async getFirstCommitWithVersion(branch, submodule, version) {
        const logs = await this.getLogs(branch, submodule);
        for (const log of logs) {
            if (log.message.includes(version)) {
                return log.hash;
            }
        }
        return null;
}}

// ... rest of the script