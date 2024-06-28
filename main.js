// main.js
const path = require("path");
const { app, BrowserWindow, ipcMain, shell } = require("electron");
const { dialog } = require("electron");
const fs = require("fs");

// Global Variables:

/**
 * The main window of the application.
 * @type {Object}
 */
let mainWindow;

/**
 * Represents the structure of a repository.
 * @typedef {Object} RepoStruct
 * @property {string} repoPath - The path of the repository.
 * @property {null|RepoHandler} repoHandler - The handler for the repository.
 */
const repoStruct = {
  repoPath: "",
  repoHandler: null,
};

/**
 * The logger variable is used for logging messages.
 * @type {Logger}
 */
let logger;

/**
 * The file path for the version finder settings file.
 * @type {string}
 */
const settingsPath = path.join(
  app.getPath("userData"),
  "version-finder-settings.json"
);

/**
 * Regular expression pattern used to extract the dot notation version from a string.
 * @type {RegExp}
 */
const DEFAULT_SEARCH_PATTERN_DOT_NOTATION_VERSION_REGEX =
  /Version: (\d+\.\d+\.\d+)/;

/**
 * Regular expression pattern used to match version numbers in the format XX_0_0_0.
 * @type {RegExp}
 */
const DEFAULT_SEARCH_PATTERN_UNDERSCORE_NOTATION_VERSION_REGEX =
  /Version: (XX_\d+_\d+_\d+)/;

/**
 * Object representing the settings.
 * @type {Object}
 */
let settings = {};

/**
 * Indicates whether the application is running in development mode.
 * @type {boolean}
 */
const isDevMode = process.env.NODE_ENV === "development";

// Functions:: Settings related functions

/**
 * Deletes the settings file if it exists.
 */
function deleteSettingsFile() {
  if (fs.existsSync(settingsPath)) {
    fs.unlinkSync(settingsPath);
  }
}

/**
 * Creates the default search pattern settings.
 * @returns {Array} The default search pattern settings.
 */
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

/**
 * Creates default logger settings.
 * @returns {Object} The default logger settings.
 */
function createDefaultLoggerSettings() {
  const os = require("os");
  const tempDir = os.tmpdir();
  const timeString = new Date()
    .toISOString()
    .replace(/:/g, "-")
    .replace(/\./g, "-");
  const logFilePath = `${tempDir}/version_finder_${timeString}.log`;
  const settings_logger_options = {
    logLevel: isDevMode ? "debug" : "info",
    logFile: logFilePath,
    logConsole: isDevMode,
  };
  return settings_logger_options;
}

/**
 * Creates a default settings file if it does not exist.
 */
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

/**
 * Initializes the logger with the specified options.
 *
 * @param {Object} loggerOptions - The options for configuring the logger.
 * @param {string} [loggerOptions.logFile] - The path to the log file.
 * @param {boolean} [loggerOptions.logConsole] - Whether to log to the console.
 * @param {string} [loggerOptions.logLevel] - The log level to set for the logger.
 * @returns {Object} - The initialized logger object.
 */
function initializeLogger(loggerOptions) {
  const {
    addFileTransport,
    addConsoleTransport,
    logger,
  } = require("./logger.js");

  // Initialize the logger
  logger.clear();

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

/**
 * Initializes the settings for the application.
 * If in development mode, deletes the settings file.
 * Creates a default settings file if it does not exist.
 * Reads the search pattern from the settings file.
 * Initializes the logger.
 */
function initializeSettings() {
  if (isDevMode) {
    deleteSettingsFile();
  }
  // Create a default settings file if it does not exist
  createDefaultSettingsFile();

  // Read the search pattern from the settings file
  settings = JSON.parse(fs.readFileSync(settingsPath));

  // Initialize the logger
  logger = initializeLogger(settings.loggerOptions);
}

initializeSettings();

function createMainWindow() {
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
  createMainWindow();

  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
  });
});

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});

// Main IPC code
ipcMain.on("init:repo", async (e, options) => {
  logger.info("Got into init:repo");
  logger.debug("repoStruct.repoPath: ", repoStruct.repoPath);
  logger.debug("options.repoPath: ", options.repoPath);

  // Check if the repo was already initialized
  if (
    repoStruct.repoHandler &&
    repoStruct.repoPath &&
    repoStruct.repoPath === options.repoPath
  ) {
    logger.debug("repoStruct: ", repoStruct.repoPath);
    logger.debug("Repo already initialized");
    mainWindow.webContents.send("init:done");
    return;
  } else {
    const form = {
      repositoryPath: options.repoPath,
    };
    logger.info(form);
    await initRepo({ form });
  }
});

ipcMain.on("search:version", (e, options) => {
  logger.info("Got into search:version");
  logger.info("options: ", options);
  searchVersion(options);
});

async function initRepo({ form }) {
  if (!form.repositoryPath) {
    sendError("Invalid repository path", new Error("Repository path is empty"));
    return null;
  }
  if (!fs.existsSync(form.repositoryPath)) {
    sendError(
      "Invalid repository path",
      new Error("Repository path does not exist")
    );
    return null;
  }
  if (
    repoStruct.repoHandler &&
    repoStruct.repoPath &&
    repoStruct.repoPath == form.repositoryPath
  ) {
    logger.info("Repo already initialized");
    logger.debug("repoStruct: ", repoStruct);

    mainWindow.webContents.send("init:done");
    return true;
  }

  try {
    const { VersionFinder } = require("./version_finder.js");
    const versionFinder = new VersionFinder(form.repositoryPath);
    await versionFinder.init().then(() => {
      logger.info("init done");
      const branches = versionFinder.getBranches();
      const submodules = versionFinder.getSubmodules();
      logger.info("from initRepo: branches: ", branches);
      logger.info("from initRepo: submodules: ", submodules);
      mainWindow.webContents.send("init:done::updated-lists", {
        branches,
        submodules,
      });
      repoStruct.repoPath = form.repositoryPath;
      repoStruct.repoHandler = versionFinder;
      return true;
    });
  } catch (err) {
    sendError("Failed to initialize repository", err);
    return null;
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
    console.log("versionFinder: ", versionFinder);
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
    if (
      err.message ==
      "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
    ) {
      const action_button = {
        label: "Stash changes",
        action: "save-repo-state",
      };
      sendWarning("Git repository has uncommitted changes.", action_button);
    } else {
      sendError("Invalid commit SHA", err);
    }
    return;
  }
  // Try and get first version commit
  try {
    if (searchResultStructure.isValidFirstCommit) {
      console.log("versionFinder: ", versionFinder);
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
        const version = result.message.match(
          versionFinder.searchPatternRegex
        )[1];
        searchResultStructure.isValidVersionCommit = true;
        searchResultStructure.shortShaVersionCommit = commit_hash;
        searchResultStructure.commitMessageVersionCommit = commit_message;
        searchResultStructure.version = version;
      }
    }
    mainWindow.webContents.send("search:done", searchResultStructure);
    return searchResultStructure; // Return the result from the function
  } catch (err) {
    sendError("Invalid commit SHA", err);
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
    let versionFinder;
    if (!form.repositoryPath) {
      sendError(
        "Invalid repository path",
        new Error("Repository path is empty")
      );
      return;
    }
    if (repoStruct.repoHandler && repoStruct.repoPath == form.repositoryPath) {
      logger.info("Repo already initialized");
      versionFinder = repoStruct.repoHandler;
    } else {
      const { VersionFinder } = require("./version_finder.js");
      versionFinder = new VersionFinder(form.repositoryPath);
    }
    const searchPattern = getSelectedSearchPattern();
    logger.info("searchPattern: ", searchPattern);
    versionFinder.setSearchPattern(searchPattern);
    await versionFinder.init().then(async () => {
      logger.info("init done");
      repoStruct.repoHandler = versionFinder;
      await findFirstCommit(versionFinder, form);
    });
    await repoStruct.repoHandler.restoreRepoSnapshot();
  } catch (err) {
    sendError("Failed to initialize repository", err);
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
 * @param {string} message - The error message.
 * @param {Object} error - The error object.
 */
function sendError(message, error) {
  console.error(message, error);
  console.error("message: ", error.message);
  console.error("stack: ", error.stack);
  // Convert the error object into a plain object including message and stack
  const errorToSend = {
    message: error.message,
    stack: error.stack,
    // Include any other properties you need
  };
  mainWindow.webContents.send("error", {
    message,
    error: errorToSend,
  });
}

function sendWarning(message, action_button) {
  console.warn(message, action_button);
  console.warn("label: ", action_button.label);
  console.warn("action: ", action_button.action);
  // Convert the error object into a plain object including message and stack
  const actionButtonToSend = {
    label: action_button.label,
    action: action_button.action,
    // Include any other properties you need
  };
  mainWindow.webContents.send("warning", {
    message,
    action_button: actionButtonToSend,
  });
}

let settingsWindow;

ipcMain.on("open-settings", () => {
  if (!settingsWindow) {
    settingsWindow = new BrowserWindow({
      width: 1200,
      height: 800,
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
ipcMain.on("open:log-file", () => {
  logger.info("Got into open:log-file");
  shell.openPath(settings.loggerOptions.logFile);
});

ipcMain.on("update-logger-configurations", (event, { type, value }) => {
  // Check if the type is valid to avoid updating non-existing properties
  if (["logLevel", "logConsole", "logFile"].includes(type)) {
    // Update the corresponding setting
    settings.loggerOptions[type] = value;
    // Reinitialize the logger with updated settings
    initializeLogger(settings.loggerOptions);
  } else {
    console.error(`Invalid logger configuration type: ${type}`);
  }
});

ipcMain.on("save-repo-state", async () => {
  logger.info("save-repo-state");

  // Check if the repo was already initialized
  if (repoStruct.repoHandler && repoStruct.repoPath) {
    await repoStruct.repoHandler.saveRepoSnapshot();
    mainWindow.webContents.send("save-repo-state:done");
    return;
  }
});
