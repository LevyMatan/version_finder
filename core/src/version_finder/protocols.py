# version_finder/protocols.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Version:
    """Represents a semantic version"""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    @classmethod
    def from_string(cls, version_str: str) -> 'Version':
        """Parse version string into Version object"""
        import re

        pattern = r"""
            ^
            (?P<major>0|[1-9]\d*)\.
            (?P<minor>0|[1-9]\d*)\.
            (?P<patch>0|[1-9]\d*)
            (?:-(?P<prerelease>
                (?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)
                (?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*
            ))?
            (?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?
            $
        """
        match = re.match(pattern, version_str.strip(), re.VERBOSE)
        if not match:
            raise ValueError(f"Invalid version string: {version_str}")

        return cls(
            major=int(match.group('major')),
            minor=int(match.group('minor')),
            patch=int(match.group('patch')),
            prerelease=match.group('prerelease'),
            build=match.group('build')
        )
