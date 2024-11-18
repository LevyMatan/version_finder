
# Version Finder

Version Finder is a command-line utility for finding and comparing versions in Git repositories. It provides an easy way to manage and analyze version information across multiple branches and submodules.

## Installation

To install Version Finder, follow these steps:

1. Ensure you have Python 3.6 or higher installed on your system.
2. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/version_finder.git
   cd version_finder
   ```

3. Install the package using pip:

   ```bash
   pip install .
   ```

## Usage

After installation, you can use the `version_finder` command-line tool. Here are some example commands:

```bash
version_finder -p /path/to/repo                 # Find versions in specified repository
version_finder -v                               # Run with verbose output
version_finder --timeout 60                     # Set git operation timeout to 60 seconds
```

For a full list of options, run:

```bash
version_finder --help
```

## Features

- Find and compare versions across different branches in a Git repository
- Handle Git submodules
- Verify commit signatures
- Retrieve detailed commit information

## Code Structure

The Version Finder utility is structured as follows:

- `version_finder/__main__.py`: Contains the main CLI logic and argument parsing
- `version_finder/core.py`: Implements the `VersionFinder` class, which handles Git operations
- `version_finder/logger.py`: Sets up logging for the application
- `version_finder/protocols.py`: Defines protocol classes for type hinting

### Core Components

1. `VersionFinder` class:
   - Manages Git repository operations
   - Handles submodules and branches
   - Performs version comparisons and retrieves commit information

2. CLI Interface:
   - Parses command-line arguments
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
4. Install the package in editable mode: `pip install -e .[dev]`
5. Run tests: `pytest ./tests`
6. flake8: `flake8 ./src/`
7. flake8: `flake8 ./tests/`
8. autopep8: `autopep8 --in-place --aggressive --max-line-length 120 src/**/*.py`
9. autopep8: `autopep8 --in-place --aggressive --max-line-length 120 tests/**/*.py`

Before submitting a pull request, please ensure that all tests pass and the code adheres to the project's coding standards.

## License

[Include license information here]
