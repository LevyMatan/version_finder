from version_finder.__version__ import __version__
import subprocess
import re


def test_version_format():
    assert __version__ is not None
    assert len(__version__) > 0
    assert __version__.count(".") == 2


def test_version_command():
    # Run the GUI command
    result = subprocess.run(
        ["version-finder", "--version"],
        capture_output=True,
        text=True
    )

    # Check that the command returned successfully
    assert result.returncode == 0

    # Parse the version from the output
    # Actual output is like "version_finder gui-v1.2.3"
    version_pattern = r"version_finder v(\d+\.\d+\.\d+)"
    match = re.search(version_pattern, result.stdout)

    assert match is not None, f"Version pattern not found in output: {result.stdout}"

    # Extract the version from the match
    core_version = match.group(1)

    # Compare with expected version
    expected_version = __version__
    assert core_version == expected_version, f"Core version {core_version} doesn't match package version {expected_version}"
