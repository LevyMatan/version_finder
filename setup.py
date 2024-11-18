# setup.py
import os
from setuptools import setup, find_packages


def get_version():
    """
    Retrieves the version string from the `_version.py` file located in the `version_finder` module.

    Returns:
        str: The version string.

    Raises:
        RuntimeError: If the version string cannot be found in the `_version.py` file.
    """
    version_file = os.path.join(
        os.path.dirname(__file__),
        'src',
        'version_finder',
        '_version.py'
    )
    with open(version_file) as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")


setup(
    name="version-finder",
    version=get_version(),
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "prompt_toolkit>=3.0.0",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "flake8", "autopep8"],  # Development tools
        "docs": ["sphinx", "sphinx_rtd_theme"],  # Documentation tools
    },
    entry_points={
        "console_scripts": [
            "version-finder=version_finder.__main__:main",
        ],
    },
    author="Matan Levy",
    description="A utility for finding versions in Git repositories",
    python_requires=">=3.6",
)
