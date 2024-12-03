module.exports = {
    branches: ["main"], // Branches to release from
    plugins: [
      // Generate changelog
      [
        "@semantic-release/changelog",
        {
          changelogFile: "CHANGELOG.md",
        },
      ],
      // Update version in Python files
      [
        "@semantic-release/exec",
        {
          prepareCmd: "sed -i 's/^__version__ = .*/__version__ = \"${nextRelease.version}\"/' core/src/version_finder/__version__.py",
        },
      ],
      // Commit changelog and updated files
      [
        "@semantic-release/git",
        {
          assets: ["CHANGELOG.md", "core/src/version_finder/__version__.py"],
          message: "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
        },
      ],
      // Publish to PyPI
      [
        "@semantic-release/exec",
        {
          publishCmd: "python -m build && twine upload dist/* -u __token__ -p $PYPI_API_TOKEN",
          buildCmd: "python -m build",
        },
      ],
      // Create a GitHub release
      "@semantic-release/github",
    ],
  };
