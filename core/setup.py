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
        '__version__.py'
    )
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")


setup(
    name="version-finder-git-based-versions",
    version=get_version(),
    description="A library for finding versions in Git repositories",
    author="Matan Levy",
    author_email="levymatanlevy@gmail.com",
    url="https://github.com/LevyMatan/version_finder",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    long_description=open("README.md").read(),  # Detailed description (e.g., README.md)
    long_description_content_type="text/markdown",  # Content type of long description
    license="MIT",  # License information
    install_requires=[
        "platformdirs",
    ],
    extras_require={
        "dev": ["pytest", "pytest-xdist", "pytest-cov", "flake8", "autopep8"],  # Development tools
    },
    entry_points={
        "console_scripts": [
            "version-finder=version_finder.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
