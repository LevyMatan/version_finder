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
    let selected_submodule = null;

    if (submoduleList.value != 'No submodules in Repository') {
        selected_submodule = submoduleList.value;
    }

    const commitSHA = commitSHAList.value
    const searchParams = {
        repositoryPath,
        branch,
        submodule: selected_submodule,
        commitSHA,
    }
    console.log("searchParams: ", searchParams)
    ipcRenderer.send('search:version', searchParams);
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

    // Disable the branch and submodule input fields
    document.getElementById('branch-name-input').disabled = true;
    document.getElementById('submodule-name-input').disabled = true;

});

ipcRenderer.on('search:done', (event, args) => {
    console.log("search done in renderer.js");
    console.log(args);

    // Update the modal content based on the results
    setModalInfo(args);
    // Show the modal
    var myModal = new bootstrap.Modal(document.getElementById('resultModal'));
    myModal.show();
});

document.addEventListener("DOMContentLoaded", setModalInfo({
    isValidFirstCommit: true, // Change to false to test the error message
    shortShaFirstCommit: "abc123",
    commitMessageFirstCommit: "Initial commit",
    isValidVersionCommit: true, // Change to false to test the error message
    shortShaVersionCommit: "3498t69784kjsdjkv",
    commitMessageVersionCommit: "Version: 1.0.0",
    version: "1.0.0"
}))
function setModalInfo(results) {
    // Clear all modal content
    document.getElementById("firstCommitSha").textContent = '';
    document.getElementById("firstCommitMessage").textContent = '';
    document.getElementById("versionCommitSha").textContent = '';
    document.getElementById("versionCommitMessage").textContent = '';
    document.getElementById("versionInfo").textContent = '';
    document.getElementById("errorMessage").style.display = "none";
    document.getElementById("validResultsFirstCommit").style.display = "none";
    document.getElementById("validResultsVersion").style.display = "none";

    // Update the modal content based on the results
    if (results.isValidFirstCommit) {
        document.getElementById("firstCommitSha").textContent = `${results.shortShaFirstCommit}`;
        document.getElementById("firstCommitMessage").textContent = `${results.commitMessageFirstCommit}`;
        document.getElementById("validResultsFirstCommit").style.display = "block";
        if (results.isValidVersionCommit) {
            document.getElementById("versionCommitSha").textContent = `${results.shortShaVersionCommit}`;
            document.getElementById("versionCommitMessage").textContent = `${results.commitMessageVersionCommit}`;
            document.getElementById("versionInfo").textContent = results.version;
            document.getElementById("validResultsVersion").style.display = "block";
        }
    } else {
        document.getElementById("errorMessage").style.display = "block";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Find all elements with the class 'clickable-sha'
    document.querySelectorAll('.clickable-sha').forEach(function(element) {
      element.addEventListener('click', function() {
        // Copy the text of the clicked element to the clipboard
        navigator.clipboard.writeText(this.textContent).then(() => {
          alert("SHA copied to clipboard!");
        }, () => {
          alert("Failed to copy SHA.");
        });
      });
    });
  });