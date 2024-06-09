// main.js
const path = require('path')
const os = require('os')
const { app, BrowserWindow, Menu, ipcMain, shell } = require('electron')
const VersionFinder = require('./version_finder.js')

let mainWindow;

const isDevMode = process.env.NODE_ENV === 'development'
console.log("isDevMode: ", isDevMode)

function createWindow () {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, 'icon-jinny.icns')
})

    // Open the DevTools when the app is started
  mainWindow.loadFile('index.html')
  if (isDevMode){
    mainWindow.webContents.openDevTools()
  }
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})


// Main IPC code
ipcMain.on('init:repo', (e, options) => {
    console.log("Got into init:repo")
    const form = {
        repositoryPath: options.repoPath,
    }
    console.log(form)
    initRepo({ form })
})

ipcMain.on('search:version', (e, options) => {
    console.log("Got into search:version")
    const form = {
        repositoryPath: options.repositoryPath,
        repositoryBranch: options.branch,
        submodule: options.submodule,
        commitSHA: options.commitSHA,
    }
    console.log(form)
    searchVersion({ form })
})

async function initRepo({ form }) {
    try {
        const versionFinder = new VersionFinder(form.repositoryPath)
        await versionFinder.init()
        .then((err) => {
            if (err) {
                throw err;
            }
            console.log("init done")
            const branches = versionFinder.getBranches()
            const submodules = versionFinder.getSubmodules()
            console.log("from initRepo: branches: ", branches)
            console.log("from initRepo: submodules: ", submodules)
            mainWindow.webContents.send('init:done', { branches, submodules })
        })
        .catch((err) => {
            console.log("init error: ", err)
            mainWindow.webContents.send('init:error:invalid-repo-path', { error: err })
        })
    } catch (err) {
        console.error(err)
    }
}


async function findFirstCommit(versionFinder, form) {
    try {
        const result = await versionFinder.getFirstCommitWithVersion(form.commitSHA, form.repositoryBranch, form.submodule);
        console.log("search done");
        console.log("result: ", result);
        // Handle case the result is null
        if (!result) {
            mainWindow.webContents.send('search:error:version-not-found', { error: 'Version not found in commit messages.' });
            return null;
        }
        mainWindow.webContents.send('search:done', { commitSHA: result });
        return result; // Return the result from the function
    } catch (err) {
        console.log("search error: ", err);
        mainWindow.webContents.send('search:error:invalid-commit-sha', { error: err });
        throw err; // Rethrow the error if you want to allow the caller to handle it
    }
}
/**
 * Searches for a version using the provided form data.
 * @param {Object} options - The options object.
 * @param {Object} options.form - The form data.
 * @param {string} options.form.repositoryPath - The path to the repository.
 * @param {string} options.form.commitSHA - The commit SHA.
 * @param {string} options.form.repositoryBranch - The repository branch.
 * @param {string} options.form.submodule - The submodule.
 */
async function searchVersion({ form }) {
    try {
        const versionFinder = new VersionFinder(form.repositoryPath)
        await versionFinder.init()
        .then((err) => {
            if (err) {
                throw err;
            }
            console.log("init done")
        })
        .catch((err) => {
            console.log("init error: ", err)
            mainWindow.webContents.send('init:error:invalid-repo-path', { error: err })
        })

        findFirstCommit(versionFinder, form)

    } catch (err) {
        console.error(err)
    }


}
