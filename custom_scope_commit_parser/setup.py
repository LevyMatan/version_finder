"""
setup.py for version_finder
This file is used to package and distribute the version_finder module.
"""
from setuptools import setup, find_packages

setup(
    name="custom-scope-commit-parser",
    version="1.0.0",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    install_requires=[],
    description="Custom Commit Parser: to fillter by scope",
    author="Matan Levy",
    author_email="levymatanlevy@gmail.com",
    url="https://github.com/LevyMatan/version_finder",
    license="MIT",  # License information
    python_requires=">=3.7",
)
