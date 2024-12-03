# Semantic Release Usage Guide

This project uses semantic-release to manage version updates across multiple packages. Here's how to use it effectively:

## Commit Messages

Use the following prefixes to trigger version updates for specific packages:

- `cli:` - For CLI package changes
- `core:` - For core package changes
- `gui:` - For GUI package changes

Combined with conventional commit types:

```
<package>: <type>(<scope>): <description>

Examples:
cli: feat(parser): add new command line argument
core: fix(finder): resolve version detection bug
gui: perf(ui): improve rendering performance
```

## Types of Changes

- `feat:` - New features (triggers minor version bump)
- `fix:` - Bug fixes (triggers patch version bump)
- `BREAKING CHANGE:` - Breaking changes (triggers major version bump)
- Other types: `build:`, `ci:`, `docs:`, `perf:`, `refactor:`, `style:`, `test:`

## Version Updates

The semantic-release workflow will:
1. Detect which package changed based on commit prefixes
2. Update the appropriate version numbers
3. Update both pyproject.toml and __version__.py files
4. Create appropriate git tags
5. Generate release notes