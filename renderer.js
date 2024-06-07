// renderer.js
const { ipcRenderer } = require('electron');

const form = document.getElementById('version-finder-form');
const repositoryPathInput = document.getElementById('repo-path');
repositoryPathInput.value = __dirname;
const resultParagraph = document.getElementById('version-result');
const branchList = document.getElementById('branch-name-input');
const submoduleList = document.getElementById('submodule-name-input');
const commitSHAList = document.getElementById('commit-sha');
commitSHAList.value = 'HEAD~1';

function resetForm() {
    // Clear the result paragraph
    resultParagraph.innerHTML = '';
    // Clear branch and submodule input fields
    document.getElementById('branch-name-input').value = 'Please type to choose a branch';
    document.getElementById('submodule-name-input').value = 'Please type to choose a submodule';
    document.getElementById('commit-sha').value = 'HEAD~1';
    // Set branch and submodule to enabled
    document.getElementById('branch-name-input').disabled = false;
    document.getElementById('submodule-name-input').disabled = false;
}
/**
 * Listen for the change event on the file input field
 */
document.getElementById('repo-browser').addEventListener('change', function() {
    if (this.files && this.files[0]) {
        var path = this.files[0].path;
        var directory = path.split('/').slice(0, -1).join('/');
        console.log("directory: ", path);
        repositoryPathInput.value = directory;

        resetForm();
        // Send the repository path to the main process
        sendInitRepoEvent();
    }
});

/**
 * Send the repository path to the main process
 */
function sendInitRepoEvent() {
    // Get the repository path from the input field
    const repositoryPath = repositoryPathInput.value;

    console.log("repositoryPath: ", repositoryPath);

    ipcRenderer.send('init:repo', {
        repoPath: repositoryPath,
    });
}

/**
 * Send the selected branch and submodule to the main process
 */
function sendSearchVersion() {
    const repositoryPath = repositoryPathInput.value;
    const branch = branchList.value;
    const submodule = null;

    if (submoduleList.value !== 'No submodules in Repository') {
        const submodule = submoduleList.value;
    }

    const commitSHA = commitSHAList.value
    ipcRenderer.send('search:version', {
        repositoryPath,
        branch,
        submodule,
        commitSHA,
    });
}

/**
 * Listen for the form submission event
 */
form.addEventListener('submit', (event) => {
    // Prevent the form from submitting normally
    event.preventDefault();

    sendSearchVersion();
});

/**
 * When the DOM is ready, init the repository
*/
document.addEventListener('DOMContentLoaded', function() {
    sendInitRepoEvent();
});

ipcRenderer.on('init:done', (event, args) => {

    console.log("init done in renderer.js")
    console.log(args);

    // Update the branch and submodule list
    updateBranchAndSubmoduleList(args["branches"], args["submodules"]);

    // If the only submodule is 'No submodules in Repo', disable the submodule input,
    // and set the value to 'No submodules in Repository'
    if (args.submodules[0] === 'No submodules in Repo') {
        document.getElementById('submodule-name-input').disabled = true;
        document.getElementById('submodule-name-input').value = 'No submodules in Repository';
    }

    // If master or main is in the branch list, set it as the default value
    if (args.branches.includes('master')) {
        document.getElementById('branch-name-input').value = 'master';
    } else if (args.branches.includes('main')) {
        document.getElementById('branch-name-input').value = 'main';
    }
});

function updateBranchList(branchList) {
    console.log("updateBranchList");
    console.log(branchList);

    const branchListElement = document.getElementById('branches-list');
    branchListElement.innerHTML = '';

    branchList.forEach((branch) => {
        const branchElement = document.createElement('option');
        branchElement.innerHTML = branch;
        branchListElement.appendChild(branchElement);
    });

}

function updateSubmoduleList(submoduleList) {
    console.log("updateSubmoduleList");
    console.log(submoduleList);
    const submoduleListElement = document.getElementById('submodules-list');
    submoduleListElement.innerHTML = '';

    submoduleList.forEach((submodule) => {
        const submoduleElement = document.createElement('option');
        submoduleElement.innerHTML = submodule;
        submoduleListElement.appendChild(submoduleElement);
    });
}

function updateBranchAndSubmoduleList(branchList, submoduleList) {
    console.log("updateBranchAndSubmoduleList");
    updateBranchList(branchList);
    updateSubmoduleList(submoduleList);
}
ipcRenderer.on('init:error:invalid-repo-path', (event) => {
    console.log("init error in renderer.js")
    console.log(event);
    resultParagraph.innerHTML = 'Invalid repository path';
    // Set to red and bold
    resultParagraph.style.color = 'red';
    resultParagraph.style.fontWeight = 'bold';

    // Disable the branch and submodule input fields
    document.getElementById('branch-name-input').disabled = true;
    document.getElementById('submodule-name-input').disabled = true;

});

ipcRenderer.on('search:done', (event, args) => {
    console.log("search done in renderer.js")
    console.log(args);
    resultParagraph.innerHTML = args.commitSHA;
    // Set to green and bold
    resultParagraph.style.color = 'green';
    resultParagraph.style.fontWeight = 'bold';
    });
