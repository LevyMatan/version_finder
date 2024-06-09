// renderer.js
const { ipcRenderer } = require('electron');

const form = document.getElementById('version-finder-form');
const repositoryPathInput = document.getElementById('repo-path');
repositoryPathInput.value = __dirname;
const branchList = document.getElementById('branch-name-input');
const submoduleList = document.getElementById('submodule-name-input');
const commitSHAList = document.getElementById('commit-sha');
commitSHAList.value = 'HEAD~1';

function resetForm() {
    branchList.value = '';
    submoduleList.value = '';
    commitSHAList.value = 'HEAD~1';
    branchList.disabled = submoduleList.disabled = false;
}

function sendInitRepoEvent() {
    ipcRenderer.send('init:repo', { repoPath: repositoryPathInput.value });
}

function sendSearchVersion() {
    const searchParams = {
        repositoryPath: repositoryPathInput.value,
        branch: branchList.value,
        submodule: submoduleList.value !== 'No submodules in Repository' ? submoduleList.value : null,
        commitSHA: commitSHAList.value,
    };
    ipcRenderer.send('search:version', searchParams);
}

function updateList(elementId, items) {
    const listElement = document.getElementById(elementId);
    listElement.innerHTML = '';
    items.forEach(item => {
        const optionElement = document.createElement('option');
        optionElement.textContent = item;
        listElement.appendChild(optionElement);
    });
}

function setModalInfo(results) {
    clearModalContent();

    if (results.isValidFirstCommit) {
        if (results.isValidFirstCommit) {
            const validResultsFirstCommit = document.getElementById("validResultsFirstCommit");
            validResultsFirstCommit.style.display = "block";
        }
        const firstCommitShaElement = document.getElementById("firstCommitSha");
        if (firstCommitShaElement){
            firstCommitShaElement.textContent = results.shortShaFirstCommit;
            firstCommitShaElement.style.display = "block";
        }

        const firstCommitMessage = document.getElementById("firstCommitMessage");
        if (firstCommitMessage){
            firstCommitMessage.textContent = "Commit Message:" +  results.commitMessageFirstCommit;
            firstCommitMessage.style.display = "block";
        }

        if (results.isValidVersionCommit) {
            const versionCommitSha = document.getElementById("versionCommitSha");
            const versionCommitMessage = document.getElementById("versionCommitMessage");
            const versionInfo = document.getElementById("versionInfo");
            const validResultsVersion = document.getElementById("validResultsVersion");
            if (versionCommitSha && versionCommitMessage && versionInfo && validResultsVersion) {
                versionCommitSha.textContent = results.shortShaVersionCommit;
                versionCommitMessage.textContent = "Commit Message:" + results.commitMessageVersionCommit;
                versionInfo.textContent = "Version: " + results.version;
                validResultsVersion.style.display = "block";
                versionCommitSha.style.display = versionCommitMessage.style.display = versionInfo.style.display = "block";
            }
        }
    } else {
        const errorMessage = document.getElementById("errorMessage");
        if (errorMessage) {
            errorMessage.style.display = "block";
        }
    }
}

function clearModalContent() {
    ["firstCommitSha", "firstCommitMessage", "versionCommitSha", "versionCommitMessage", "versionInfo", "errorMessage", "validResultsFirstCommit", "validResultsVersion"].forEach(id => {
        const element = document.getElementById(id);
        element.style.display = 'none';
    });
}

function initializeTooltipAndCopyFunctionality(buttonId, textElementId, successMessage, originalMessage) {
    const button = document.getElementById(buttonId);
    const textElement = document.getElementById(textElementId);
    const tooltip = new bootstrap.Tooltip(button, { title: originalMessage, trigger: "hover" });

    button.addEventListener('click', () => {
        navigator.clipboard.writeText(textElement.textContent).then(() => {
            button.setAttribute('data-bs-original-title', successMessage);
            tooltip.show();
            setTimeout(() => resetTooltip(button, tooltip, originalMessage), 2000);
        }).catch(err => console.error('Error copying text: ', err));
    });
}

function resetTooltip(button, tooltip, originalMessage) {
    button.setAttribute('data-bs-original-title', originalMessage);
    tooltip.hide();
}

document.addEventListener('DOMContentLoaded', () => {
    sendInitRepoEvent();
    initializeTooltipAndCopyFunctionality('copyButton', 'firstCommitSha', 'Copied!', 'Copy to clipboard');
    initializeTooltipAndCopyFunctionality('versionCopyButton', 'versionCommitSha', 'Copied!', 'Copy to clipboard');
});

document.getElementById('repo-browser').addEventListener('change', function() {
    if (this.files && this.files[0]) {
        const selectedFilePath = this.files[0].path;
        const directory = selectedFilePath.split('/').slice(0, -1).join('/');
        repositoryPathInput.value = directory;
        resetForm();
        sendInitRepoEvent();
    }
});

form.addEventListener('submit', (event) => {
    event.preventDefault();
    sendSearchVersion();
});

ipcRenderer.on('init:done', (event, args) => {
    updateList('branches-list', args.branches);
    updateList('submodules-list', args.submodules);
    if (args.submodules[0] === 'No submodules in Repo') {
        submoduleList.disabled = true;
        submoduleList.value = 'No submodules in Repository';
    }
    branchList.value = args.branches.includes('master') ? 'master' : args.branches.includes('main') ? 'main' : '';
});

ipcRenderer.on('init:error:invalid-repo-path', () => {
    branchList.disabled = submoduleList.disabled = true;
});

ipcRenderer.on('search:done', (event, args) => {
    new bootstrap.Modal(document.getElementById('resultModal')).show();
    setModalInfo(args);
});