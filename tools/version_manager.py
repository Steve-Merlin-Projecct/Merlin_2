#!/usr/bin/env python3
"""
Version Manager - Centralized version control for the project

This script manages the project version number stored in the VERSION file
and updates all references throughout the codebase.

Usage:
    python tools/version_manager.py                    # Show current version
    python tools/version_manager.py --bump minor       # Bump patch version (4.0.1 -> 4.0.2)
    python tools/version_manager.py --bump mid         # Bump minor version (4.0.1 -> 4.1.0)
    python tools/version_manager.py --bump major       # Bump major version (4.0.1 -> 5.0.0)
    python tools/version_manager.py --set 4.1.0        # Set specific version
    python tools/version_manager.py --sync             # Sync version to all files
"""

import sys
import os
import re
from pathlib import Path
from typing import Tuple


class VersionManager:
    """Manages project version across multiple files"""

    def __init__(self, root_dir: Path = None):
        """Initialize version manager"""
        if root_dir is None:
            # Assume script is in tools/ directory
            self.root_dir = Path(__file__).parent.parent
        else:
            self.root_dir = Path(root_dir)

        self.version_file = self.root_dir / "VERSION"

    def get_current_version(self) -> str:
        """Read current version from VERSION file"""
        if not self.version_file.exists():
            raise FileNotFoundError(f"VERSION file not found at {self.version_file}")

        with open(self.version_file, 'r') as f:
            version = f.read().strip()

        if not self._is_valid_version(version):
            raise ValueError(f"Invalid version format in VERSION file: {version}")

        return version

    def set_version(self, version: str) -> None:
        """Set version in VERSION file"""
        if not self._is_valid_version(version):
            raise ValueError(f"Invalid version format: {version}")

        with open(self.version_file, 'w') as f:
            f.write(version)

        print(f"✅ Version set to: {version}")

    def bump_version(self, bump_type: str) -> str:
        """
        Bump version number

        Args:
            bump_type: 'major' (+.0.0), 'mid' (x.+.0), or 'minor' (x.x.+)

        Returns:
            str: New version number
        """
        current = self.get_current_version()
        major, minor, patch = self._parse_version(current)

        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'mid':
            minor += 1
            patch = 0
        elif bump_type == 'minor':
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}. Use 'major', 'mid', or 'minor'")

        new_version = f"{major}.{minor}.{patch}"
        self.set_version(new_version)
        return new_version

    def sync_to_files(self) -> None:
        """Sync version to all files that reference it"""
        version = self.get_current_version()
        print(f"🔄 Syncing version {version} to all files...")

        updated_files = []

        # Update CLAUDE.md
        claude_md = self.root_dir / "CLAUDE.md"
        if claude_md.exists():
            if self._update_claude_md(claude_md, version):
                updated_files.append("CLAUDE.md")

        # Update pyproject.toml
        pyproject = self.root_dir / "pyproject.toml"
        if pyproject.exists():
            if self._update_pyproject_toml(pyproject, version):
                updated_files.append("pyproject.toml")

        # Update .env.example
        env_example = self.root_dir / ".env.example"
        if env_example.exists():
            if self._update_env_example(env_example, version):
                updated_files.append(".env.example")

        # Update app_modular.py (if it has version)
        app_file = self.root_dir / "app_modular.py"
        if app_file.exists():
            if self._update_app_version(app_file, version):
                updated_files.append("app_modular.py")

        if updated_files:
            print(f"✅ Updated version in: {', '.join(updated_files)}")
        else:
            print("ℹ️  No files needed updating")

    def _update_claude_md(self, file_path: Path, version: str) -> bool:
        """Update version in CLAUDE.md"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Pattern: Version X.Y.Z - Claude Code Edition
        pattern = r'Version \d+\.\d+\.\d+ - Claude Code Edition'
        new_text = f'Version {version} - Claude Code Edition'

        if pattern in content or re.search(pattern, content):
            new_content = re.sub(pattern, new_text, content)

            if new_content != content:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                return True

        return False

    def _update_pyproject_toml(self, file_path: Path, version: str) -> bool:
        """Update version in pyproject.toml"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Pattern: version = "X.Y.Z"
        pattern = r'version = "[^"]+"'
        new_text = f'version = "{version}"'

        new_content = re.sub(pattern, new_text, content, count=1)

        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True

        return False

    def _update_env_example(self, file_path: Path, version: str) -> bool:
        """Update version in .env.example"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if version variable exists, if not add it
        if 'PROJECT_VERSION' not in content:
            # Add to application settings section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '# APPLICATION SETTINGS' in line:
                    # Insert after this section header
                    lines.insert(i + 1, '')
                    lines.insert(i + 2, f'PROJECT_VERSION={version}')
                    new_content = '\n'.join(lines)

                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    return True
        else:
            # Update existing version
            pattern = r'PROJECT_VERSION=.*'
            new_text = f'PROJECT_VERSION={version}'
            new_content = re.sub(pattern, new_text, content)

            if new_content != content:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                return True

        return False

    def _update_app_version(self, file_path: Path, version: str) -> bool:
        """Update version in app_modular.py"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if __version__ exists
        if '__version__' not in content:
            # Add at the top after imports
            lines = content.split('\n')
            # Find first non-import, non-comment line
            insert_index = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('import') and not stripped.startswith('from'):
                    insert_index = i
                    break

            lines.insert(insert_index, f'__version__ = "{version}"')
            lines.insert(insert_index + 1, '')
            new_content = '\n'.join(lines)

            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
        else:
            # Update existing version
            pattern = r'__version__ = "[^"]+"'
            new_text = f'__version__ = "{version}"'
            new_content = re.sub(pattern, new_text, content)

            if new_content != content:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                return True

        return False

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version string is valid (semantic versioning)"""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    @staticmethod
    def _parse_version(version: str) -> Tuple[int, int, int]:
        """Parse version string into (major, minor, patch)"""
        parts = version.split('.')
        return int(parts[0]), int(parts[1]), int(parts[2])


def main():
    """CLI interface for version manager"""
    manager = VersionManager()

    if len(sys.argv) == 1:
        # Show current version
        try:
            version = manager.get_current_version()
            print(f"Current version: {version}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif sys.argv[1] == '--bump' and len(sys.argv) == 3:
        # Bump version
        bump_type = sys.argv[2]
        try:
            old_version = manager.get_current_version()
            new_version = manager.bump_version(bump_type)
            print(f"🎉 Version bumped: {old_version} -> {new_version}")
            print("\n📝 Next steps:")
            print(f"   1. Run: python tools/version_manager.py --sync")
            print(f"   2. Review changes")
            print(f"   3. Commit: git add . && git commit -m 'Bump version to {new_version}'")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif sys.argv[1] == '--set' and len(sys.argv) == 3:
        # Set specific version
        version = sys.argv[2]
        try:
            manager.set_version(version)
            print("\n📝 Next steps:")
            print(f"   1. Run: python tools/version_manager.py --sync")
            print(f"   2. Review changes")
            print(f"   3. Commit: git add . && git commit -m 'Set version to {version}'")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif sys.argv[1] == '--sync':
        # Sync version to all files
        try:
            manager.sync_to_files()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
