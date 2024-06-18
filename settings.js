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
    console.error("Element not found for selector:", selector);
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
