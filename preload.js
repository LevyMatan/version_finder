// preload.js
const { contextBridge, ipcRenderer } = require('electron')
const VersionFinder = require('./version_finder.js')

contextBridge.exposeInMainWorld(
  'electron',
  {
    require: require,
  }
)
