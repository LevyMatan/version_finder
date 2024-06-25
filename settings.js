// settings.js
const { ipcRenderer } = require("electron");
const settingsForm = document.getElementById("settingsForm");

let settings = {};

// Assuming loggerOptions is an object with your logger settings
function updateLoggerConfiguration(type, value) {
  ipcRenderer.send("update-logger-configurations", { type, value });
}

window.onload = () => {
  settings = ipcRenderer.sendSync("get-settings");
  console.log("settings.js: get-settings");
  console.log("settings: ", settings);

  if (settings && settings.searchPatternOptions) {
    const searchPatternOptions = settings.searchPatternOptions;
    const searchPatternInputGroup = document.getElementById(
      "searchPatternInputGroup"
    );

    // For each searchPatternOptions, create a radio button with a label, wrapped in a div
    const container = document.createElement("div"); // Container for all options

    searchPatternOptions.forEach((option, index) => {
      const formCheckDiv = document.createElement("div");
      formCheckDiv.className = "form-check";

      const input = document.createElement("input");
      input.type = "radio";
      input.name = "searchPattern";
      input.value = option.value;
      input.id = option.value;
      input.className = "form-check-input";
      if (option.isChecked) input.checked = true;

      const label = document.createElement("label");
      label.htmlFor = option.value;
      label.className = "form-check-label";
      label.textContent = `${option.text}`;

      const p = document.createElement("p");
      p.className = "d-inline-flex gap-1";

      const a = document.createElement("a");
      // <i class="fa-regular fa-lightbulb"></i>
      a.className = "fas fa-chevron-down";
      a.title = "Show RegEx"; // Adding a tooltip
      a.setAttribute("data-bs-toggle", "collapse");
      a.setAttribute("data-bs-target", `#collapseExample${index}`); // Use data-bs-target instead of href
      a.role = "button";
      a.setAttribute("aria-expanded", "false");
      a.setAttribute("aria-controls", `collapseExample${index}`);
      a.textContent = "";

      const collapseDiv = document.createElement("div");
      collapseDiv.className = "collapse";
      collapseDiv.id = `collapseExample${index}`;

      const cardBodyDiv = document.createElement("div");
      cardBodyDiv.className = "card card-body";
      cardBodyDiv.textContent = option.value;

      // Assemble the elements
      collapseDiv.appendChild(cardBodyDiv);
      p.appendChild(label);
      p.appendChild(a);
      formCheckDiv.appendChild(input);
      formCheckDiv.appendChild(p);
      formCheckDiv.appendChild(collapseDiv);
      container.appendChild(formCheckDiv);
    });
    searchPatternInputGroup.appendChild(container);

    // In the searchPatternInputGroup, I would like to let the user add a new pattern
    // Below the last radio button, I would like to add a button that says "Add new pattern"
    // Once clicked, the Add new pattern should be replaced with a single line the has:
    // 1. A text input field for the pattern name
    // 2. A text input field for the RegEx pattern
    // 3. A button that says "Create new pattern"
    // Once the "Create new pattern" button is clicked, the new pattern should be added to the searchPatternOptions
    // and the radio buttons should be updated to include the new pattern
    // and the "Add new pattern" button should be added back to the end of the radio buttons

    // to implement this, I would like to create a new div, that will hold two divs and toggle the display of the divs
    // The first div will hold the "Add new pattern" button
    // The second div will hold the text input fields and the "Create new pattern" button
    const addNewPatternDiv = document.createElement("div");

    const newPatternButtonDiv = document.createElement("div");
    newPatternButtonDiv.id = "newPatternButtonDiv";

    const addNewPatternButton = document.createElement("button");
    addNewPatternButton.className = "btn btn-primary";
    addNewPatternButton.textContent = "Add new pattern";
    addNewPatternButton.addEventListener("click", (e) => {
      e.preventDefault();
      console.log("Add new pattern clicked");
      document.getElementById("newPatternButtonDiv").style.display = "none";
      newPatternDiv.style.display = "flex"; // Use Flexbox to align children in a row
      newPatternDiv.style.gap = "10px"; // Optional: add some space between the children
    });
    newPatternButtonDiv.appendChild(addNewPatternButton);
    addNewPatternDiv.appendChild(newPatternButtonDiv);

    const newPatternDiv = document.createElement("div");
    newPatternDiv.style.display = "none";

    const newPatternName = document.createElement("input");
    newPatternName.type = "text";
    newPatternName.className = "form-control";
    newPatternName.placeholder = "Pattern Name";
    newPatternDiv.appendChild(newPatternName);
    const newPatternRegEx = document.createElement("input");
    newPatternRegEx.type = "text";
    newPatternRegEx.className = "form-control";
    newPatternRegEx.placeholder = "RegEx Pattern";
    newPatternDiv.appendChild(newPatternRegEx);
    const createNewPatternButton = document.createElement("button");
    createNewPatternButton.className = "btn btn-primary";
    createNewPatternButton.textContent = "Create new pattern";
    createNewPatternButton.addEventListener("click", (e) => {
      e.preventDefault();
      const newPattern = {
        text: newPatternName.value,
        value: newPatternRegEx.value,
        isChecked: false,
      };
      searchPatternOptions.push(newPattern);
      newPatternDiv.style.display = "none";
      newPatternButtonDiv.style.display = "block";
      newPatternName.value = "";
      newPatternRegEx.value = "";
    });

    newPatternDiv.appendChild(createNewPatternButton);
    addNewPatternDiv.appendChild(newPatternDiv);
    searchPatternInputGroup.appendChild(addNewPatternDiv);

    // Manually initialize collapse components for dynamically added elements
    document.querySelectorAll(".collapse").forEach((collapseElement) => {
      new bootstrap.Collapse(collapseElement, {
        toggle: false, // This ensures the collapse elements are not toggled automatically upon initialization
      });
    });
    // Add listener events for the radio buttons
    // When they are changed, update the settings object
    document.querySelectorAll("input[type=radio]").forEach((radio) => {
      radio.addEventListener("change", (e) => {
        console.log("radio changed:", e.target.value);
        settings.searchPatternOptions.forEach((option) => {
          option.isChecked = option.value === e.target.value;
        });
      });
    });
  } else {
    console.error("Element not found for selector:", "input[type=radio]");
  }

  if (settings && settings.loggerOptions) {
    // There are three logger options:
    // 1. Log level: input of type select from all the options available in Winston
    // 2. File to log to: path input field
    // 3. Console logging: checkbox
    // For each of these options, set the value to the value in settings
    // The loggerOptions object has the following structure:
    // {
    //   logLevel: string,
    //   logFile: string,
    //   logConsole: boolean,
    // }
    // The expected layout is:
    // Log Level
    // Choose the most verbose level you would like to log, all levels below this will be logged as well
    // Select log level: [dropdown]
    //
    // Log File
    // Choose location to save log file (please provide full path)
    // [file input field]
    //
    // Log to Console
    // Toggle whether to log all meassages both to the file and the console
    // [checkbox] Log to console

    const loggerOptions = settings.loggerOptions;

    // Create a div to hold the logger options
    const loggerOptionsDiv = document.getElementById("loggerInputGroup");

    // LogLevelDiv will contain:
    // <div class="mb-3">
    //   <label for="logLevelSelectInput" class="form-label">Log Level</label>
    //   <input type="select" class="form-control" id="logLevelSelectInput" aria-describedby="logLevelHelp">
    //   <div id="logLevelHelp" class="form-text">Choose the most verbose level you would like to log, all levels below this will be logged as well.</div>
    // </div>

    const logLevelDiv = document.createElement("div");
    logLevelDiv.className = "mb-3";
    const logLevelLabel = document.createElement("label");
    logLevelLabel.textContent = "Log Verbosity Level";
    logLevelLabel.htmlFor = "logLevelSelectInput"; // Adjusted to match the comment
    logLevelLabel.className = "form-label";
    logLevelDiv.appendChild(logLevelLabel);

    const logLevelSelect = document.createElement("select"); // Corrected element creation
    logLevelSelect.className = "form-control";
    logLevelSelect.id = "logLevelSelectInput"; // Adjusted to match the comment
    logLevelSelect.ariaDescribedby = "logLevelHelp"; // Correct attribute name and match the comment
    logLevelSelect.name = "logLevel";
    logLevelSelect.required = true;
    logLevelSelect.addEventListener("change", (e) => {
      loggerOptions.logLevel = e.target.value;
      updateLoggerConfiguration("logLevel", loggerOptions.logLevel);
    });
    const logLevels = [
      "error",
      "warn",
      "info",
      "http",
      "verbose",
      "debug",
      "silly",
    ];
    logLevels.forEach((level) => {
      const option = document.createElement("option");
      option.value = level;
      option.textContent = level;
      if (level === loggerOptions.logLevel) option.selected = true;
      logLevelSelect.appendChild(option);
    });
    logLevelDiv.appendChild(logLevelSelect);

    const logLevelHelp = document.createElement("div"); // Corrected element creation
    logLevelHelp.id = "logLevelHelp"; // Adjusted to match the comment
    logLevelHelp.className = "form-text settings-input-helper";
    logLevelHelp.textContent =
      "Choose the most verbose level you would like to log, all levels below this will be logged as well.";
    logLevelDiv.appendChild(logLevelHelp);

    loggerOptionsDiv.appendChild(logLevelDiv);

    // logFileDiv will contain:
    // <div class="mb-3">
    //   <label for="logFileInput" class="form-label">Log File</label>
    //   <input type="file" class="form-control" id="logFileInput" aria-describedby="logFileHelp">
    //   <div id="logFileHelp" class="form-text">Choose location to save log file (please provide full path).</div>
    // </div>
    // Create the container div
    const logFileDiv = document.createElement("div");
    logFileDiv.className = "mb-3";
    logFileDiv.style.position = "relative";
    logFileDiv.style.display = "inline-block";

    // Create and append the label
    const logFileLabel = document.createElement("label");
    logFileLabel.className = "form-label";
    logFileLabel.textContent = "Log File";
    logFileLabel.htmlFor = "logFileInput";
    logFileDiv.appendChild(logFileLabel);

    // Create the file input
    const logFileInput = document.createElement("input");
    logFileInput.type = "file";
    logFileInput.className = "form-control";
    logFileInput.id = "logFileInput";
    logFileInput.ariaDescribedby = "logFileHelp";
    logFileDiv.appendChild(logFileInput);

    // Create the text input for displaying the file name
    const fileNameDisplay = document.createElement("input");
    fileNameDisplay.type = "text";
    fileNameDisplay.className = "form-control";
    fileNameDisplay.id = "fileNameDisplay";
    fileNameDisplay.style.position = "absolute";
    fileNameDisplay.style.top = "0";
    fileNameDisplay.style.left = "0";
    fileNameDisplay.style.width = "100%";
    fileNameDisplay.readOnly = true;
    fileNameDisplay.value = loggerOptions.logFile;
    logFileDiv.appendChild(fileNameDisplay);

    // Create and append the helper div
    const logFileHelp = document.createElement("div");
    logFileHelp.id = "logFileHelp";
    logFileHelp.className = "form-text settings-input-helper";
    logFileHelp.textContent =
      "Choose location to save log file (please provide full path).";
    logFileDiv.appendChild(logFileHelp);

    // Append the container to the loggerOptionsDiv or any other desired parent element
    loggerOptionsDiv.appendChild(logFileDiv);

    // Event listener to update the text input with the file name when a file is selected
    logFileInput.addEventListener("change", function () {
      if (this.files.length > 0) {
        fileNameDisplay.value = this.files[0].name;
      }
      loggerOptions.logFile = this.files[0].path;
      updateLoggerConfiguration("logFile", loggerOptions.logFile);
    });

    // logConsoleDiv will contain:
    // <div class="mb-3">
    //   <label for="logConsoleInput" class="form-label">Log File</label>
    //   <input type="check" class="form-control" id="logConsoleInput" aria-describedby="logConsoleHelp">
    //   <div id="logConsoleHelp" class="form-text">Toggle whether to log all meassages both to the file and the console.</div>
    // </div>
    const logConsoleDiv = document.createElement("div");
    logConsoleDiv.className = "mb-3";

    const logConsoleLabel = document.createElement("label");
    logConsoleLabel.textContent = " Log to Console"; // Temporarily hold the label text
    logConsoleLabel.className = "form-label";
    logConsoleLabel.htmlFor = "logConsoleInput";

    // Create the checkbox input
    const logConsoleInput = document.createElement("input");
    logConsoleInput.type = "checkbox";
    logConsoleInput.id = "logConsoleInput";
    logConsoleInput.ariaDescribedby = "logConsoleHelp";
    logConsoleInput.checked = loggerOptions.logConsole;
    logConsoleInput.addEventListener("change", (e) => {
      loggerOptions.logConsole = e.target.checked;
      updateLoggerConfiguration("logConsole", loggerOptions.logConsole);
    });

    // Insert the checkbox at the beginning of the label element
    logConsoleLabel.insertBefore(logConsoleInput, logConsoleLabel.firstChild);

    const logConsoleHelp = document.createElement("div");
    logConsoleHelp.id = "logConsoleHelp";
    logConsoleHelp.className = "form-text settings-input-helper";
    logConsoleHelp.textContent =
      "Toggle whether to log all messages both to the file and the console.";

    logConsoleDiv.appendChild(logConsoleLabel); // Now the label contains the checkbox
    logConsoleDiv.appendChild(logConsoleHelp);

    loggerOptionsDiv.appendChild(logConsoleDiv);

    // Add a button to open the log file and display the logs in a table (using DataTables)
    const openLogFileButton = document.createElement("button");
    openLogFileButton.className = "btn btn-primary";
    openLogFileButton.textContent = "Open Log File";
    openLogFileButton.addEventListener("click", (e) => {
      e.preventDefault();
      ipcRenderer.send("open:log-file", loggerOptions.logFile);
    });
    loggerOptionsDiv.appendChild(openLogFileButton);
  }
};

// Add this at the end of settings.js
const closeButton = document.getElementById("closeButton");

// Save settings when the form is submitted
settingsForm.addEventListener("submit", (e) => {
  console.log("settingsForm submitted");
  e.preventDefault();
  ipcRenderer.send("save-settings", settings);
  closeButton.click();
});

closeButton.addEventListener("click", () => {
  ipcRenderer.send("close-settings");
});
