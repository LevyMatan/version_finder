// settings.js
const { ipcRenderer } = require('electron');
const settingsForm = document.getElementById('settingsForm');

let settings = {};

window.onload = () => {
  settings = ipcRenderer.sendSync('get-settings');
  console.log('settings.js: get-settings');
  console.log('settings: ', settings);

  if (settings && settings.searchPatternOptions) {
    const searchPatternOptions = settings.searchPatternOptions;
    const searchPatternInputGroup = document.getElementById('searchPatternInputGroup');

    // For each searchPatternOptions, create a radio button with a label, wrapped in a div
    searchPatternOptions.forEach((option) => {
      const container = document.createElement('div'); // Container for each radio button and label
      container.classList.add('form-check'); // Optional: Bootstrap class for better styling

      const radio = document.createElement('input');
      radio.type = 'radio';
      radio.name = 'searchPattern';
      radio.value = option.value;
      radio.id = option.value;
      radio.checked = option.isChecked;
      radio.classList.add('form-check-input'); // Optional: Bootstrap class for better styling

      const label = document.createElement('label');
      label.htmlFor = option.value;
      label.classList.add('form-check-label'); // Optional: Bootstrap class for better styling
      label.appendChild(document.createTextNode(option.text + ": " + option.value));

      container.appendChild(radio);
      container.appendChild(label);

      searchPatternInputGroup.appendChild(container);
    });

    // Add listener events for the radio buttons
    // When they are changed, update the settings object
    document.querySelectorAll('input[type=radio]').forEach((radio) => {
      radio.addEventListener('change', (e) => {
        console.log('radio changed:', e.target.value);
        settings.searchPatternOptions.forEach((option) => {
          option.isChecked = option.value === e.target.value;
        });
      });
    });
  } else {
    console.error('Element not found for selector:', selector);
  }
};

// Save settings when the form is submitted
settingsForm.addEventListener('submit', (e) => {
  console.log('settingsForm submitted');
  e.preventDefault();
  ipcRenderer.send('save-settings', settings);
});

// Add this at the end of settings.js
const closeButton = document.getElementById('closeButton');

closeButton.addEventListener('click', () => {
  ipcRenderer.send('close-settings');
});
