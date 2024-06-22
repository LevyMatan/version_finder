// main.js
const path = require("path");
const { app, BrowserWindow, ipcMain, shell } = require("electron");
const { dialog } = require("electron");
const fs = require("fs");

let mainWindow;

const settingsPath = path.join(
  app.getPath("userData"),
  "version-finder-settings.json"
);

const DEFAULT_SEARCH_PATTERN_DOT_NOTATION_VERSION_REGEX =
  /Version: (\d+\.\d+\.\d+)/;
const DEFAULT_SEARCH_PATTERN_UNDERSCORE_NOTATION_VERSION_REGEX =
  /Version: (XX_\d+_\d+_\d+)/;
let settings = {};
const isDevMode = process.env.NODE_ENV === "development";

function deleteSettingsFile() {
  if (fs.existsSync(settingsPath)) {
    fs.unlinkSync(settingsPath);
  }
}

function createDefaultSearchPatternSettings() {
  let settings_search_pattern_html_form_options = [];
  settings_search_pattern_html_form_options.push({
    value: DEFAULT_SEARCH_PATTERN_DOT_NOTATION_VERSION_REGEX.toString(),
    text: "Dot Notation (e.g. 1.0.0)",
    isChecked: false,
  });
  settings_search_pattern_html_form_options.push({
    value: DEFAULT_SEARCH_PATTERN_UNDERSCORE_NOTATION_VERSION_REGEX.toString(),
    text: "Underscore Notation (e.g. XX_1_0_0)",
    isChecked: true,
  });
  return settings_search_pattern_html_form_options;
}

function createDefaultLoggerSettings() {
  const os = require('os');
  const tempDir = os.tmpdir();
  const timeString = new Date().toISOString().replace(/:/g, '-').replace(/\./g, '-');
  const logFilePath = `${tempDir}/version_finder_${timeString}.log`;
  const settings_logger_options = {
    logLevel: isDevMode ? "debug": "info",
    logFile: logFilePath,
    logConsole: isDevMode,
  }
  return settings_logger_options;
}

function createDefaultSettingsFile() {
  // Create a default settings file if it does not exist
  if (!fs.existsSync(settingsPath)) {
    // Create the logger options
    settings.loggerOptions = createDefaultLoggerSettings();
    // Create the searchPattern form options
    settings.searchPatternOptions = createDefaultSearchPatternSettings();
    // Write the settings to the file
    fs.writeFileSync(settingsPath, JSON.stringify(settings));
  }
}

function initializeSettings() {
  if (isDevMode) {
    deleteSettingsFile();
  }
  // Create a default settings file if it does not exist
  createDefaultSettingsFile();

  // Read the search pattern from the settings file
  settings = JSON.parse(fs.readFileSync(settingsPath));
}

initializeSettings();

function initializeLogger(loggerOptions) {
  const { addFileTransport, addConsoleTransport, logger} = require("./logger.js");

  if (loggerOptions.logFile) {
    addFileTransport(logger, loggerOptions.logFile);
  }
  if (loggerOptions.logConsole) {
    addConsoleTransport(logger);
  }
  if (loggerOptions.logLevel) {
    logger.level = loggerOptions.logLevel;
  }
  logger.info("Logger initialized");

  return logger;

}
const logger = initializeLogger(settings.loggerOptions);

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
  logger.info("Got into init:repo");
  const form = {
    repositoryPath: options.repoPath,
  };
  logger.info(form);
  initRepo({ form });
});

ipcMain.on("search:version", (e, options) => {
  logger.info("Got into search:version");
  logger.info("options: ", options);
  searchVersion(options);
});

async function initRepo({ form }) {
  try {
    const VersionFinder = require("./version_finder.js");
    const versionFinder = new VersionFinder(form.repositoryPath);
    await versionFinder
      .init()
      .then(() => {
        logger.info("init done");
        const branches = versionFinder.getBranches();
        const submodules = versionFinder.getSubmodules();
        logger.info("from initRepo: branches: ", branches);
        logger.info("from initRepo: submodules: ", submodules);
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
  logger.info("Entered findFirstCommit");
  logger.info("form: ", form);
  try {
    const firstCommitstruct = await versionFinder.getFirstCommitSha(
      form.commitSHA,
      form.branch,
      form.submodule
    );
    logger.info("firstCommitstruct: ", firstCommitstruct);
    if (firstCommitstruct) {
      searchResultStructure.isValidFirstCommit = true;
      searchResultStructure.shortShaFirstCommit = firstCommitstruct.hash; // Ensure this matches the property name in firstCommitstruct
      searchResultStructure.commitMessageFirstCommit =
        firstCommitstruct.message; // Ensure this matches the property name in firstCommitstruct
    } else {
      searchResultStructure.isValidFirstCommit = false;
    }
    logger.info("searchResultStructure: ", searchResultStructure);
  } catch (err) {
    sendError("search:error:invalid-commit-sha", "Invalid commit SHA", err);
    return;
  }
  // Try and get first version commit
  try {
    if (searchResultStructure.isValidFirstCommit) {
      const result = await versionFinder.getFirstCommitWithVersion(
        searchResultStructure.shortShaFirstCommit,
        form.branch,
        form.submodule
      );
      logger.info("search done");
      logger.info("result: ", result);

      // Handle case the result is null
      if (result) {
        const commit_hash = result.hash;
        const commit_message = result.message;
        const version = result.message.match(versionFinder.searchPatternRegex)[1];
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
  logger.info("form = ", form);
  try {
    const VersionFinder = require("./version_finder.js");
    const versionFinder = new VersionFinder(form.repositoryPath);
    const searchPattern = getSelectedSearchPattern();
    logger.info("searchPattern: ", searchPattern);
    versionFinder.setSearchPattern(searchPattern);
    await versionFinder
      .init()
      .then(() => {
        logger.info("init done");
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
  logger.info("Got into open:directory");
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
  });

  logger.info("Selected directory: ", result);

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

let settingsWindow;

ipcMain.on("open-settings", () => {
  if (!settingsWindow) {
    settingsWindow = new BrowserWindow({
      width: 800,
      height: 600,
      parent: mainWindow, // Assuming mainWindow is your main app window
      modal: true,
      show: false,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false,
      },
    });

    settingsWindow.loadFile("settings.html");
    settingsWindow.once("ready-to-show", () => {
      settingsWindow.show();
      if (isDevMode) {
        settingsWindow.webContents.openDevTools();
      }
    });

    settingsWindow.on("closed", () => {
      settingsWindow = null;
    });
  }
});

ipcMain.on("get-settings", (event) => {
  try {
    // Verify file exists before reading
    if (!fs.existsSync(settingsPath)) {
      throw new Error("Settings file does not exist");
    }
    settings = JSON.parse(fs.readFileSync(settingsPath));
  } catch (err) {
    console.error("Failed to read settings:", err);
  }
  logger.info("ipcMain: get-settings");
  logger.info("settings: ", settings);
  event.returnValue = settings;
});

ipcMain.on("save-settings", (event, newSettings) => {
  logger.info("ipcMain: save-settings");
  logger.info("newSettings: ", newSettings);
  try {
    logger.info("Saving to settings file:", settingsPath);
    fs.writeFileSync(settingsPath, JSON.stringify(newSettings));
  } catch (err) {
    console.error("Failed to save settings:", err);
  }
});

// Add this inside the main.js, where you have other ipcMain handlers
ipcMain.on("close-settings", () => {
  logger.info("Close settings window");
  if (settingsWindow) {
    settingsWindow.close();
  }
});

function getSelectedSearchPattern() {
  try {
    // Verify file exists before reading
    if (!fs.existsSync(settingsPath)) {
      throw new Error("Settings file does not exist");
    }
    settings = JSON.parse(fs.readFileSync(settingsPath));
  } catch (err) {
    console.error("Failed to read settings:", err);
  }

  for (const option of settings.searchPatternOptions) {
    logger.info("option: ", option);
    if (option.isChecked) {
      logger.info("getSelectedSearchPattern: option.value: ", option.value);
      return option.value;
    }
  }
  // Optional: Return a default value or null if no option is checked
  return null;
}

// Hanlde the open:log-file event
ipcMain.on("open:log-file", (event) => {
  logger.info("Got into open:log-file");
  shell.openPath(settings.loggerOptions.logFile);
}
);
