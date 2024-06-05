// renderer.js
const path = require('path');
const os = require('os');
const { ipcRenderer } = require('electron');

// When DOM is ready:
// 1. Initialize the VersionFinder class
// 2. Send the repository path to the main process
// 3. Listen for the reply from the main process
// 4. Update the UI with the branches and submodules
// 5. Listen for the form submission event
// 6. Get the selected branch and submodule
// 7. Send the selected branch and submodule to the main process
// 8. Listen for the reply from the main process
// 9. Update the UI with the commit SHA
// 10. Listen for the form submission event
// 11. Get the selected commit SHA
// 12. Send the selected commit SHA to the main process
// 13. Listen for the reply from the main process
// 14. Update the UI with the commit details


const form = document.getElementById('version-finder-form');
const repositoryBrowser = document.getElementById('repo-browser');
const repositoryPathInput = document.getElementById('repo-path');
repositoryPathInput.value = __dirname;
const resultParagraph = document.getElementById('version-result');
const branchList = document.getElementById('branch-name-input');
const submoduleList = document.getElementById('submodule-name-input');

// Update the repository path when a directory is selected
document.getElementById('repo-browser').addEventListener('change', function() {
    event.preventDefault();
    if (this.files && this.files[0]) {
        var path = this.files[0].path;
        var directory = path.split('/').slice(0, -1).join('/');
        console.log("directory: ", path);
        repositoryPathInput.value = directory;
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
    const submodule = submoduleList.value;
    const commitSHA = 'HEAD~3';
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
    // Create an options Object to pass into the M.Autocomplete.init() function
    const options_branches = {
        data: {
            ...args["branches"].reduce((obj, branch) => ({ ...obj, [branch]: null }), {}),
        },
    };
    const options_submodules = {
        data: {
            ...args.submodules.reduce((obj, submodule) => ({ ...obj, [submodule]: null }), {}),
        },
    };
    var auto_branch = document.querySelectorAll('.autocomplete-branch');
    M.Autocomplete.init(auto_branch, options_branches);
    // Set the value of the first branch
    if (args["branches"].length > 0) {
        auto_branch[0].value = args["branches"][0];
    }
    var auto_submodule = document.querySelectorAll('.autocomplete-submodule');
    M.Autocomplete.init(auto_submodule, options_submodules);
    // Set the value of the first submodule
    if (args.submodules.length > 0) {
        auto_submodule[0].value = args.submodules[0];
    }
});

ipcRenderer.on('init:error:invalid-repo-path', (event) => {
    console.log("init error in renderer.js")
    console.log(event);
    resultParagraph.innerHTML = 'Invalid repository path';
    // Set to red and bold
    resultParagraph.style.color = 'red';
    resultParagraph.style.fontWeight = 'bold';

});
