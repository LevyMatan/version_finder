# Version Finder

![App Logo](assets/icons/version-finder-iconset/icon.iconset/icon_256x256.png)

The Version Finder is a tool designed to help developers determine the earliest version (commit or tag) in which a specific commit from a submodule was introduced in a Git project. It’s particularly useful when working with projects that use submodules and need to track the history of submodule changes.

There are two flavors for the Version Finder tool:

- [version_finder.py](version_finder.py): A command-line tool that fetches information about submodules and branches from the main project repository.
- Electron based app: A graphical user interface (GUI) version of the tool that provides a more user-friendly experience.

## Features

- Fetches information about submodules and branches from the main project repository.
- Allows the user to select a specific branch and submodule.
- Accepts a commit SHA as input.
- Determines the earliest version where the given submodule commit appears.

## CLI

### Prerequisites

- Python 3.x
- Git (installed and configured)

### Installation and Usage

Using the CLI option:

- Download the version_finder.py script.
- Open a terminal and navigate to the project directory.
- Run the version_finder.py script.

   ```bash
   python version_finder.py
   ```

- Follow the prompts to provide the necessary information:
  - Choose a branch.
  - Enter the submodule path (e.g., sub-module-A).
  - Supply the commit SHA.
- The tool will display the earliest version where the specified submodule commit appears.

#### Example

```bash
$ python version_finder.py

Available submodules:
- sub-module-A
- sub-module-B

Available branches:
- main
- feature/awesome-feature
- release/v1.0

Enter the branch name: main
Enter the submodule path: sub-module-A
Enter the commit SHA: abc123456

Submodule commit abc123456 introduced in version: 1234567 (commit message)
```

Notes
Make sure you have the necessary permissions to access the Git repository.
The tool assumes that the submodule commit exists in the main project’s history.
License
This project is licensed under the MIT License - see the LICENSE file for details.

## Electron App

The Electron app provides a graphical user interface (GUI) for the Version Finder tool. It offers a more user-friendly experience and is suitable for users who prefer a visual interface.

### Installation

Download the latest version of the app from the [Releases](https://github.com/LevyMatan/version_finder/releases) page.
Please note that the app is only available for macOS and Linux.
