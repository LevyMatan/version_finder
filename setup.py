"""
setup.py for version_finder
This file is used to package and distribute the version_finder module.
"""
import os
from setuptools import setup, find_packages


def get_version():
    """
    Retrieves the version string from `__init__.py` file located in the version_finder module.

    Returns:
        str: The version string.

    Raises:
        RuntimeError: If the version string cannot be found in the __init__.py file.
    """
    version_file = os.path.join(
        os.path.dirname(__file__),
        'src',
        'version_finder',
        '__init__.py'
    )
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")


setup(
    name="version-finder",
    version=get_version(),
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    extras_require={
        "dev": ["pytest", "pytest-cov", "flake8", "autopep8"],  # Development tools
        "gui": ["customtkinter", "pillow"],
        "cli": ["prompt_toolkit>=3.0.0"],
        "cli+gui": ["customtkinter", "prompt_toolkit>=3.0.0", "pillow"],
        "all": ["pytest", "pytest-cov", "flake8", "autopep8", "customtkinter", "prompt_toolkit>=3.0.0", "pillow"],
    },
    entry_points={
        "console_scripts": [
            "version-finder=version_finder.__main__:main",
            "version-finder-cli=version_finder.__cli__:main",
            "version-finder-gui=version_finder.__gui__:main",
        ],
    },
    author="Matan Levy",
    description="A utility for finding versions in Git repositories",
    python_requires=">=3.7",
)
