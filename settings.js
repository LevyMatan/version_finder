// settings.js
const { ipcRenderer } = require("electron");
const settingsForm = document.getElementById("settingsForm");

let settings = {};

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
    console.error("Element not found for selector:", selector);
  }
};

// Save settings when the form is submitted
settingsForm.addEventListener("submit", (e) => {
  console.log("settingsForm submitted");
  e.preventDefault();
  ipcRenderer.send("save-settings", settings);
});

// Add this at the end of settings.js
const closeButton = document.getElementById("closeButton");

closeButton.addEventListener("click", () => {
  ipcRenderer.send("close-settings");
});
