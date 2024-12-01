
# Version Finder

[![Coverage Report](https://img.shields.io/badge/Coverage-Report-blue)](https://LevyMatan.github.io/version_finder/)
[![Latest Release](https://img.shields.io/github/v/release/LevyMatan/version_finder)](https://github.com/LevyMatan/version_finder/releases/latest)

Version Finder is a command-line utility for finding and comparing versions in Git repositories. It provides an easy way to manage and analyze version information across multiple branches and submodules.

## Features

- Find versions across different branches and submodules in a Git repository
- Handle Git submodules
- Retrieve detailed commit information

## Installation

You can install Version Finder in two ways:

### From GitHub Release

Download the latest wheel file from the [releases page](https://github.com/LevyMatan/version_finder/releases/latest) and install with:

```bash
pip install version_finder-*.whl
```

### From Source

1. Ensure you have Python 3.6 or higher installed on your system.
2. Clone the repository:

   ```bash
   git clone https://github.com/LevyMatan/version_finder.git
   cd version_finder
   ```

3. Install the package using pip:

   ```bash
   make install
   ```

   You will be prompted to use what will be installed, the option are:
   - Core Library only
   - Core Library and CLI
   - Core Library and GUI
   - All

   Please note that this installation does not inlude the requierments for development.

## Usage

After installation, you can use the `version_finder` command-line tool. Here are some example commands:

```bash
version_finder --gui                            # Run the GUI
version-finder --cli                            # Run the CLI
version_finder -p /path/to/repo                 # Find versions in specified repository
version_finder -v                               # Run with verbose output
version_finder --timeout 60                     # Set git operation timeout to 60 seconds
```

For a full list of options, run:

```bash
version_finder --help
```

### Direct Interaction

You can invoke a simple version finder with:

```bash
version_finder -p /path/to/repo -b target_branch -c target_commit [-s submodule_path]
```

This will find the first version containing the target commit within the target branch.

### CLI

The CLI will enable user to interact with the library in a more interactive way.
The first step will be to select the repository to work on.
After that, the user will be asked to select the branch to work on.

Now the user will given the option to choose a TASK to perform.
Based on the task chosen, user will have to enter additional information.
Tasks include:

- Find the first version containing a specific commit
- Find the first version containing a specific commit in a specific submodule
- Show all commits between two versions
- Show all commits between two versions in a specific submodule

### GUI

Reveales the same functionality as the CLI, but with a GUI interface.
It also provides instant feedback for parameter correctness and hints in the form of autocomplete.

## Code Structure

The Version Finder utility is structured as follows:

- `version_finder/__main__.py`: Contains the a gateway to the library and will preform a simple task or open CLI or GUI.
- `version_finder/core.py`: Implements the `VersionFinder` class, which handles Git operations, branch handling, and version extraction.
- `version_finder/logger.py`: Sets up logging for the application
- `version_finder/protocols.py`: Defines protocol classes for type hinting
- `version_finder/__cli__.py`: Defines the CLI interface for the application
- `version_finder/__gui__.py`: Defines the GUI interface for the application
- `version_finder/__common__.py`: Defines common utility functions for both CLI and GUI

### Core Components

1. `VersionFinder` class:
   - Manages Git repository operations
   - Handles submodules and branches
   - Performs version extraction and retrieves commit information

2. CLI Interface:
   - Provides a command-line interface for interacting with the application
   - Provides an interactive interface for selecting branches
   - Executes version finding operations based on user input

## Contributing

Contributions to Version Finder are welcome! Here are some ways you can contribute:

1. Report bugs or request features by opening issues
2. Submit pull requests with bug fixes or new features
3. Improve documentation or add examples

When contributing code, please ensure that you:

- Follow the existing code style and conventions
- Write appropriate tests for new features or bug fixes
- Update the documentation as necessary

To set up a development environment:

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On Unix or MacOS: `source venv/bin/activate`
4. Install the package in editable mode: `make install-dev`
5. Run tests: `make test`
6. flake8: `make lint`
7. autopep8: `make format`
8. coverage report: `make coverage`

Before submitting a pull request, please ensure that all tests pass and the code adheres to the project's coding standards.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
