// main.js
const path = require('path')
const os = require('os')
const { app, BrowserWindow, Menu, ipcMain, shell } = require('electron')
const VersionFinder = require('./version_finder.js')

let mainWindow;

function createWindow () {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    //   preload: path.join(__dirname, 'preload.js'),
    },
    // Open the DevTools when the app is started
  })

  mainWindow.loadFile('index.html')
  mainWindow.webContents.openDevTools()

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

        await versionFinder.getFirstCommitWithVersion(form.commitSHA, form.repositoryBranch, form.submodule)
        .then((err) => {
            if (err) {
                throw err;
            }
            console.log("search done")
            mainWindow.webContents.send('search:done', { commitSHA: form.commitSHA })
        })
        .catch((err) => {
            console.log("search error: ", err)
            mainWindow.webContents.send('search:error:invalid-commit-sha', { error: err })
        })

    } catch (err) {
        console.error(err)
    }


}
