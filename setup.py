# setup.py
from setuptools import setup, find_packages
import os

def get_version():
    version_file = os.path.join(
        os.path.dirname(__file__),
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
    packages=find_packages(),
    install_requires=[
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "version-finder=version_finder.__main__:main",
        ],
    },
    author="Your Name",
    description="A tool for finding versions in Git repositories",
    python_requires=">=3.6",
)
