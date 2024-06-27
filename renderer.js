// renderer.js
const { ipcRenderer } = require("electron");
// import bootstrap from "bootstrap";
const bootstrap = require("bootstrap");

const form = document.getElementById("version-finder-form");
const repositoryPathInput = document.getElementById("repo-path");
repositoryPathInput.value = __dirname;
const branchList = document.getElementById("branch-name-input");
const submoduleList = document.getElementById("submodule-name-input");
const commitSHAList = document.getElementById("commit-sha");
commitSHAList.value = "HEAD~1";

function resetForm() {
  branchList.value = "";
  submoduleList.value = "";
  commitSHAList.value = "HEAD~1";
  branchList.disabled = submoduleList.disabled = false;
}
// Function to show the spinner and set the message
function showProcessingMessage(message) {
  document.getElementById("spinner-modal").style.display = "block"; // Show the spinner
  document.getElementById("loading-message").innerHTML = message; // Set the message
}

// Function to hide the spinner
function hideProcessingMessage() {
  document.getElementById("spinner-modal").style.display = "none"; // Hide the spinner
}

function sendInitRepoEvent() {
  showProcessingMessage("Initializing repository...");
  ipcRenderer.send("init:repo", { repoPath: repositoryPathInput.value });
}

function sendSearchVersion() {
  const searchParams = {
    repositoryPath: repositoryPathInput.value,
    branch: branchList.value,
    submodule:
      submoduleList.value !== "No submodules in Repository"
        ? submoduleList.value
        : null,
    commitSHA: commitSHAList.value,
  };
  showProcessingMessage("Searching for version...");
  ipcRenderer.send("search:version", searchParams);
}

function updateList(elementId, items) {
  const listElement = document.getElementById(elementId);
  listElement.innerHTML = "";
  items.forEach((item) => {
    const optionElement = document.createElement("option");
    optionElement.textContent = item;
    listElement.appendChild(optionElement);
  });
}

function setModalInfo(results) {
  clearModalContent();

  if (results.isValidFirstCommit) {
    if (results.isValidFirstCommit) {
      const validResultsFirstCommit = document.getElementById(
        "validResultsFirstCommit"
      );
      validResultsFirstCommit.style.display = "block";
    }
    const firstCommitShaElement = document.getElementById("firstCommitSha");
    if (firstCommitShaElement) {
      firstCommitShaElement.textContent = results.shortShaFirstCommit;
      firstCommitShaElement.style.display = "block";
    }

    const firstCommitMessage = document.getElementById("firstCommitMessage");
    if (firstCommitMessage) {
      firstCommitMessage.textContent = results.commitMessageFirstCommit;
      firstCommitMessage.style.display = "block";
    }

    if (results.isValidVersionCommit) {
      const versionCommitSha = document.getElementById("versionCommitSha");
      const versionCommitMessage = document.getElementById(
        "versionCommitMessage"
      );
      const versionInfo = document.getElementById("versionInfo");
      const validResultsVersion = document.getElementById(
        "validResultsVersion"
      );
      if (
        versionCommitSha &&
        versionCommitMessage &&
        versionInfo &&
        validResultsVersion
      ) {
        versionCommitSha.textContent = results.shortShaVersionCommit;
        versionCommitMessage.textContent = results.commitMessageVersionCommit;
        versionInfo.textContent = "Version: " + results.version;
        validResultsVersion.style.display = "block";
        versionCommitSha.style.display =
          versionCommitMessage.style.display =
          versionInfo.style.display =
            "block";
      }
    }
  } else {
    const errorMessage = document.getElementById("errorMessage");
    if (errorMessage) {
      errorMessage.style.display = "block";
    }
  }
}

function clearModalContent() {
  [
    "firstCommitSha",
    "firstCommitMessage",
    "versionCommitSha",
    "versionCommitMessage",
    "versionInfo",
    "errorMessage",
    "validResultsFirstCommit",
    "validResultsVersion",
  ].forEach((id) => {
    const element = document.getElementById(id);
    element.style.display = "none";
  });
}

function initializeTooltipAndCopyFunctionality(
  buttonId,
  textElementId,
  successMessage,
  originalMessage
) {
  const button = document.getElementById(buttonId);
  const textElement = document.getElementById(textElementId);
  const tooltip = new bootstrap.Tooltip(button, {
    title: originalMessage,
    trigger: "hover",
  });

  button.addEventListener("click", () => {
    navigator.clipboard
      .writeText(textElement.textContent)
      .then(() => {
        button.setAttribute("data-bs-original-title", successMessage);
        tooltip.show();
        setTimeout(() => resetTooltip(button, tooltip, originalMessage), 2000);
      })
      .catch((err) => console.error("Error copying text: ", err));
  });
}

function resetTooltip(button, tooltip, originalMessage) {
  button.setAttribute("data-bs-original-title", originalMessage);
  tooltip.hide();
}

document.addEventListener("DOMContentLoaded", () => {
  initializeTooltipAndCopyFunctionality(
    "copyButton",
    "firstCommitSha",
    "Copied!",
    "Copy to clipboard"
  );
  initializeTooltipAndCopyFunctionality(
    "versionCopyButton",
    "versionCommitSha",
    "Copied!",
    "Copy to clipboard"
  );

  // Add click event listeners to branch and submodule inputs
  const branchInput = document.getElementById("branch-name-input"); // Assuming the ID of the branch input is "branchInput"
  const submoduleInput = document.getElementById("submodule-name-input"); // Assuming the ID of the submodule input is "submoduleInput"

  branchInput.addEventListener("click", sendInitRepoEvent);
  submoduleInput.addEventListener("click", sendInitRepoEvent);
});

document.getElementById("open-directory-btn").addEventListener("click", () => {
  sendOpwnDirectory();
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendSearchVersion();
});

ipcRenderer.on("selected:directory", (event, selectedDirectoryPath) => {
  console.log("selected:directory", selectedDirectoryPath);

  const startTime = performance.now(); // Start timing

  // Update the input value with the selected directory
  repositoryPathInput.value = selectedDirectoryPath;
  const inputUpdateTime = performance.now(); // Time after getting the file path

  // Reset the form
  resetForm();
  const resetFormTime = performance.now(); // Time after resetting the form

  // Send the event to initialize the repository
  sendInitRepoEvent();
  const sendEventTime = performance.now(); // Time after sending the event

  // Log the time taken for each step
  console.log(`Input update: ${inputUpdateTime - startTime}ms`);
  console.log(`Form reset: ${resetFormTime - inputUpdateTime}ms`);
  console.log(`Event sending: ${sendEventTime - resetFormTime}ms`);
});

ipcRenderer.on("init:done::updated-lists", (event, args) => {
  updateList("branches-list", args.branches);
  updateList("submodules-list", args.submodules);
  if (args.submodules[0] === "No submodules in Repo") {
    submoduleList.disabled = true;
    submoduleList.value = "No submodules in Repository";
  }
  branchList.value = args.branches.includes("master")
    ? "master"
    : args.branches.includes("main")
    ? "main"
    : "";
  hideProcessingMessage();
});
ipcRenderer.on("init:done", () => {
  console.log("init:done");
  hideProcessingMessage();
});

ipcRenderer.on("init:error:invalid-repo-path", () => {
  branchList.disabled = submoduleList.disabled = true;
  hideProcessingMessage();
});

ipcRenderer.on("search:done", (event, args) => {
  new bootstrap.Modal(document.getElementById("resultModal")).show();
  setModalInfo(args);
  hideProcessingMessage();
});

function sendOpwnDirectory() {
  ipcRenderer.send("open:directory");
}

ipcRenderer.on("error", (event, { message, error }) => {
  // Hide the spinner
  hideProcessingMessage();

  // Generate a unique ID for the accordion
  const uniqueId = `error-details-${Date.now()}`;

  // Create the alert div
  const alertDiv = document.createElement("div");
  alertDiv.className = "alert alert-danger alert-dismisable text-start";
  alertDiv.role = "alert";

  // Set the inner HTML of the alert with the title, channel, message, and an accordion for more info
  alertDiv.innerHTML = `
      <strong>An error occurred</strong>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      <p>${message}</p>
      <div class="accordion accordion-flush" id="accordion-${uniqueId}" style="background-color: inherit;">
        <div class="accordion-item" style="background-color: inherit;">
          <h2 class="accordion-header" id="heading-${uniqueId}">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${uniqueId}" aria-expanded="false" aria-controls="collapse-${uniqueId}" style="background-color: inherit;">
              Click for more info
            </button>
          </h2>
          <div id="collapse-${uniqueId}" class="accordion-collapse collapse" aria-labelledby="heading-${uniqueId}" data-bs-parent="#accordion-${uniqueId}" style="background-color: inherit;">
            <div class="accordion-body" style="background-color: inherit;">
              <pre>${error.stack}</pre>
            </div>
          </div>
        </div>
      </div>
  `;

  // Append the alert div to the placeholder
  const placeholder = document.getElementById("error-alert-placeholder");
  placeholder.innerHTML = ""; // Clear previous alerts if any
  placeholder.appendChild(alertDiv);
});

ipcRenderer.on("warning", (event, { message, action_button }) => {
  console.log("Warning message received: ", message, action_button);
  // Hide the spinner
  hideProcessingMessage();

  // Generate a unique ID for the button
  const uniqueId = `action-button-${Date.now()}`;

  // Create the alert div
  const alertDiv = document.createElement("div");
  alertDiv.className = "alert alert-warning alert-dismissible text-start";
  alertDiv.role = "alert";

  // Set the inner HTML of the alert with the title, message, and a "take action" button
  alertDiv.innerHTML = `
      <strong>Warning</strong>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      <p>${message}</p>
      <button id="${uniqueId}" class="btn btn-primary">${action_button.label}</button>
  `;

  // Append the alert div to the placeholder
  const placeholder = document.getElementById("error-alert-placeholder");
  placeholder.innerHTML = ""; // Clear previous alerts if any
  placeholder.appendChild(alertDiv);

  // Optionally, add an event listener to the "take action" button
  const actionButton = document.getElementById(uniqueId);
  actionButton.addEventListener("click", () => {
    ipcRenderer.send(action_button.action);
    // Define what happens when the "take action" button is clicked
    console.log("Take action button clicked");
    // Hide the alert
    alertDiv.style.display = "none";
  });
});

document.getElementById("version-finder-form").addEventListener(
  "submit",
  function (event) {
    if (!this.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    }

    this.classList.add("was-validated");
  },
  false
);

document.getElementById("commit-sha").addEventListener("input", function () {
  const value = this.value;
  const fullCommitHashPattern = /^[0-9a-fA-F]{40}$/;
  const headPattern = /^HEAD(~[0-9]+)?$/;
  let message = "A valid commit SHA is required.";

  if (!fullCommitHashPattern.test(value) && !headPattern.test(value)) {
    if (value.startsWith("HEAD")) {
      message = "Format should be 'HEAD' or 'HEAD~[number]'.";
    } else if (value.length === 40 && !fullCommitHashPattern.test(value)) {
      message = "Full commit hash must be exactly 40 hex characters.";
    }
    this.setCustomValidity(message);
  } else {
    this.setCustomValidity("");
  }

  this.nextElementSibling.textContent = message; // Update the invalid-feedback message
});

const settingsButton = document.getElementById("settingsButton");

settingsButton.addEventListener("click", () => {
  ipcRenderer.send("open-settings");
});
