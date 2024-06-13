// main.js
const path = require("path");
const os = require("os");
const { app, BrowserWindow, Menu, ipcMain, shell } = require("electron");
const VersionFinder = require("./version_finder.js");
const { dialog } = require("electron");
const { send } = require("process");

let mainWindow;

const isDevMode = process.env.NODE_ENV === "development";
console.log("isDevMode: ", isDevMode);

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, "icon-jinny.icns"),
  });

  // Open the DevTools when the app is started
  mainWindow.loadFile("index.html");
  if (isDevMode) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});

// Main IPC code
ipcMain.on("init:repo", (e, options) => {
  console.log("Got into init:repo");
  const form = {
    repositoryPath: options.repoPath,
  };
  console.log(form);
  initRepo({ form });
});

ipcMain.on("search:version", (e, options) => {
  console.log("Got into search:version");
  console.log("options: ", options);
  searchVersion(options);
});

async function initRepo({ form }) {
  try {
    const versionFinder = new VersionFinder(form.repositoryPath);
    await versionFinder
      .init()
      .then(() => {
        console.log("init done");
        const branches = versionFinder.getBranches();
        const submodules = versionFinder.getSubmodules();
        console.log("from initRepo: branches: ", branches);
        console.log("from initRepo: submodules: ", submodules);
        mainWindow.webContents.send("init:done", { branches, submodules });
      })
      .catch((err) => {
        sendError(
          "init:error:invalid-repo-path",
          "Invalid repository path",
          err
        );
      });
  } catch (err) {
    sendError("init:error:invalid-repo-path", "Invalid repository path", err);
  }
}

/**
 * Given the input form, searches for the first commit of the super-repo that includes the submodule target commit
 * and the first super-repo version that includes the submodule target version.
 * Sends the result to the renderer process.
 * @param {*} versionFinder an instance of VersionFinder already initialized with the repository path
 * @param {*} form containing the commitSHA, repositoryBranch, and submodule
 * @returns
 */
async function findFirstCommit(versionFinder, form) {
  /**
   * The result structure to be passed should be:
   *  {
   *    isValidFirstCommit: true, // Change to false to test the error message
   *    shortShaFirstCommit: "abc123",
   *    commitMessageFirstCommit: "Initial commit",
   *    isValidVersionCommit: true, // Change to false to test the error message
   *    shortShaVersionCommit: "3498t69784kjsdjkv",
   *    commitMessageVersionCommit: "Version: 1.0.0",
   *    version: "1.0.0"
   *  };
   */

  const searchResultStructure = {
    isValidFirstCommit: false,
    shortShaFirstCommit: "",
    commitMessageFirstCommit: "",
    isValidVersionCommit: false,
    shortShaVersionCommit: "",
    commitMessageVersionCommit: "",
    version: "",
  };
  console.log("Entered findFirstCommit");
  console.log("form: ", form);
  try {
    const firstCommitstruct = await versionFinder.getFirstCommitSha(
      form.commitSHA,
      form.branch,
      form.submodule
    );
    console.log("firstCommitstruct: ", firstCommitstruct);
    if (firstCommitstruct) {
      searchResultStructure.isValidFirstCommit = true;
      searchResultStructure.shortShaFirstCommit = firstCommitstruct.hash; // Ensure this matches the property name in firstCommitstruct
      searchResultStructure.commitMessageFirstCommit =
        firstCommitstruct.message; // Ensure this matches the property name in firstCommitstruct
    } else {
      searchResultStructure.isValidFirstCommit = false;
    }
    console.log("searchResultStructure: ", searchResultStructure);
  } catch (err) {
    sendError("search:error:invalid-commit-sha", "Invalid commit SHA", err);
  }
  // Try and get first version commit
  try {
    if (searchResultStructure.isValidFirstCommit) {
      const result = await versionFinder.getFirstCommitWithVersion(
        searchResultStructure.shortShaFirstCommit,
        form.branch,
        form.submodule
      );
      console.log("search done");
      console.log("result: ", result);

      // Handle case the result is null
      if (result) {
        const commit_hash = result.hash;
        const commit_message = result.message;
        const version = result.message.match(/Version: (\d+\.\d+\.\d+)/)[1];
        searchResultStructure.isValidVersionCommit = true;
        searchResultStructure.shortShaVersionCommit = commit_hash;
        searchResultStructure.commitMessageVersionCommit = commit_message;
        searchResultStructure.version = version;
      }
    }
    mainWindow.webContents.send("search:done", searchResultStructure);
    return searchResultStructure; // Return the result from the function
  } catch (err) {
    sendError("search:error:invalid-commit-sha", "Invalid commit SHA", err);
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
async function searchVersion(form) {
  console.log("form = ", form);
  try {
    const versionFinder = new VersionFinder(form.repositoryPath);
    await versionFinder
      .init()
      .then(() => {
        console.log("init done");
        findFirstCommit(versionFinder, form);
      })
      .catch((err) => {
        sendError(
          "error:init:invalid-repo-path",
          "Invalid repository path",
          err
        );
      });
  } catch (err) {
    sendError("error:search:invalid-repo-path", "Invalid repository path", err);
  }
}

ipcMain.on("open:directory", async function () {
  console.log("Got into open:directory");
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
  });

  console.log("Selected directory: ", result);

  // Send the selected directory to the renderer process
  if (!result.canceled && result.filePaths.length > 0) {
    mainWindow.webContents.send("selected:directory", result.filePaths[0]);
  }
});

/**
 * Send error messages to the renderer process
 * @param {string} channel - The channel to send the message to.
 * @param {string} message - The error message.
 * @param {Object} error - The error object.
 */
function sendError(channel, message, error) {
  console.error(channel, message, error);
  console.error("message: ", error.message);
  console.error("stack: ", error.stack);
  // Convert the error object into a plain object including message and stack
  const errorToSend = {
    message: error.message,
    stack: error.stack,
    // Include any other properties you need
  };
  mainWindow.webContents.send("error", {
    channel,
    message,
    error: errorToSend,
  });
}
