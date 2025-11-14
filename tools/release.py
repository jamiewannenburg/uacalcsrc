#!/usr/bin/env python3
"""
Synchronize version across all project files.

This script reads the version from VERSION file and updates:
- Cargo.toml (main crate)
- uacalc_lib/Cargo.toml (Python bindings crate)
- pyproject.toml (Python package)
- python/uacalc/__init__.py (Python package __version__)

Usage:
    python tools/release.py [--check]
    
    --check: Only check if versions are in sync, don't update
"""

import re
import sys
from pathlib import Path
from typing import Tuple, Optional

# Project root directory
ROOT = Path(__file__).parent.parent

# Files to update with their version patterns
VERSION_FILES = {
    "Cargo.toml": {
        "pattern": r'^version\s*=\s*"([^"]+)"',
        "replacement": 'version = "{}"',
        "section": "[package]",
    },
    "uacalc_lib/Cargo.toml": {
        "pattern": r'^version\s*=\s*"([^"]+)"',
        "replacement": 'version = "{}"',
        "section": "[package]",
    },
    "pyproject.toml": {
        "pattern": r'^version\s*=\s*"([^"]+)"',
        "replacement": 'version = "{}"',
        "section": "[project]",
    },
    "python/uacalc/__init__.py": {
        "pattern": r'^__version__\s*=\s*"([^"]+)"',
        "replacement": '__version__ = "{}"',
    },
}


def read_version() -> str:
    """Read version from VERSION file."""
    version_file = ROOT / "VERSION"
    if not version_file.exists():
        raise FileNotFoundError(f"VERSION file not found at {version_file}")
    
    version = version_file.read_text().strip()
    if not version:
        raise ValueError("VERSION file is empty")
    
    # Validate version format (semver-like)
    if not re.match(r'^\d+\.\d+\.\d+', version):
        raise ValueError(f"Invalid version format: {version}. Expected format: X.Y.Z")
    
    return version


def update_file_version(file_path: Path, version: str, config: dict) -> Tuple[bool, Optional[str]]:
    """
    Update version in a file.
    Returns (changed, error_message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    content = file_path.read_text()
    pattern = config["pattern"]
    replacement = config["replacement"].format(version)
    
    # Check if version needs updating
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return False, f"Version pattern not found in {file_path}"
    
    current_version = match.group(1)
    if current_version == version:
        return False, None  # Already up to date
    
    # Replace version
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    file_path.write_text(new_content)
    return True, None


def sync_versions(check_only: bool = False) -> int:
    """
    Synchronize versions across all files.
    Returns 0 on success, 1 on error, 2 if check-only found mismatches.
    """
    try:
        version = read_version()
        print(f"Current version in VERSION file: {version}")
    except Exception as e:
        print(f"Error reading VERSION file: {e}", file=sys.stderr)
        return 1
    
    errors = []
    changes = []
    
    for rel_path, config in VERSION_FILES.items():
        file_path = ROOT / rel_path
        changed, error = update_file_version(file_path, version, config)
        
        if error:
            errors.append(f"{rel_path}: {error}")
        elif changed:
            if check_only:
                errors.append(f"{rel_path}: version mismatch (has different version)")
            else:
                changes.append(rel_path)
                print(f"[OK] Updated {rel_path}")
    
    if check_only:
        if errors:
            print("\nVersion mismatches found:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 2
        else:
            print("[OK] All versions are in sync")
            return 0
    
    if errors:
        print("\nErrors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    
    if changes:
        print(f"\n[OK] Updated {len(changes)} file(s)")
    else:
        print("[OK] All versions are already in sync")
    
    return 0


def main():
    """Main entry point."""
    check_only = "--check" in sys.argv
    
    if check_only:
        print("Checking version synchronization...")
    else:
        print("Synchronizing versions...")
    
    exit_code = sync_versions(check_only=check_only)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

