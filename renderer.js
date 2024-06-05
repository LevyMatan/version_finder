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

/**
 * Listen for the change event on the file input field
 */
document.getElementById('repo-browser').addEventListener('change', function() {
    if (this.files && this.files[0]) {
        var path = this.files[0].path;
        var directory = path.split('/').slice(0, -1).join('/');
        console.log("directory: ", path);
        repositoryPathInput.value = directory;

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

    // Check if there are submodules in the repository
    const noSubmodulesInRepo = args.submodules[0] === 'No submodules in Repo';

    if (!noSubmodulesInRepo) {
        var auto_submodule = document.querySelectorAll('.autocomplete-submodule');
        M.Autocomplete.init(auto_submodule, options_submodules);
        // Set the value of the first submodule
        if (args.submodules.length > 0) {
            auto_submodule[0].value = args.submodules[0];
        }
    }
    else {
        // Set the submodule input to disabled, with value: No submodules in Repository
        document.getElementById('submodule-name-input').disabled = true;
        document.getElementById('submodule-name-input').value = 'No submodules in Repository';
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

ipcRenderer.on('search:done', (event, args) => {
    console.log("search done in renderer.js")
    console.log(args);
    resultParagraph.innerHTML = args.commitSHA;
    // Set to green and bold
    resultParagraph.style.color = 'green';
    resultParagraph.style.fontWeight = 'bold';
    });
