#!/usr/bin/env python3
"""
Bump version and sync across all files.

This script updates the VERSION file and syncs the version across all project files.
Optionally creates a git tag.

Usage:
    python tools/bump_version.py <new_version> [--tag] [--commit]
    
    new_version: Version string (e.g., "0.0.2" or "0.1.0")
    --tag: Create a git tag after updating (default: false)
    --commit: Create a git commit after updating (default: false)
    --push: Push commits and tags to remote (default: false, requires --commit and/or --tag)
    
Examples:
    python tools/bump_version.py 0.0.2
    python tools/bump_version.py 0.1.0 --tag --commit
    python tools/bump_version.py 0.2.0 --tag --commit --push
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent


def validate_version(version: str) -> bool:
    """Validate version format."""
    return bool(re.match(r'^\d+\.\d+\.\d+', version))


def update_version_file(version: str) -> None:
    """Update VERSION file."""
    version_file = ROOT / "VERSION"
    version_file.write_text(f"{version}\n")
    print(f"[OK] Updated VERSION file: {version}")


def run_sync_script() -> bool:
    """Run the release.py script."""
    sync_script = ROOT / "tools" / "release.py"
    result = subprocess.run([sys.executable, str(sync_script)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error syncing versions:\n{result.stderr}", file=sys.stderr)
        return False
    
    print(result.stdout)
    return True


def git_commit(message: str) -> bool:
    """Create a git commit."""
    try:
        subprocess.run(
            ["git", "add", "VERSION", "Cargo.toml", "uacalc_lib/Cargo.toml", 
             "pyproject.toml", "python/uacalc/__init__.py"],
            check=True,
            cwd=ROOT
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            cwd=ROOT
        )
        print(f"[OK] Created commit: {message}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating commit: {e}", file=sys.stderr)
        return False


def git_tag(version: str) -> bool:
    """Create a git tag."""
    tag = f"v{version}"
    try:
        # Check if tag already exists
        result = subprocess.run(
            ["git", "rev-parse", tag],
            capture_output=True,
            cwd=ROOT
        )
        if result.returncode == 0:
            print(f"⚠ Tag {tag} already exists, skipping", file=sys.stderr)
            return False
        
        subprocess.run(
            ["git", "tag", "-a", tag, "-m", f"Release {tag}"],
            check=True,
            cwd=ROOT
        )
        print(f"[OK] Created tag: {tag}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating tag: {e}", file=sys.stderr)
        return False


def git_push(commit: bool, tag: bool) -> bool:
    """Push commits and/or tags to remote."""
    try:
        commands = []
        if commit:
            commands.append(["git", "push"])
        if tag:
            commands.append(["git", "push", "--tags"])
        
        for cmd in commands:
            subprocess.run(cmd, check=True, cwd=ROOT)
        
        if commands:
            print("[OK] Pushed to remote")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pushing to remote: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    if not validate_version(new_version):
        print(f"Error: Invalid version format: {new_version}", file=sys.stderr)
        print("Expected format: X.Y.Z (e.g., 0.0.2, 0.1.0, 1.2.3)", file=sys.stderr)
        sys.exit(1)
    
    create_tag = "--tag" in sys.argv
    create_commit = "--commit" in sys.argv
    push = "--push" in sys.argv
    
    if push and not (create_tag or create_commit):
        print("Error: --push requires --tag and/or --commit", file=sys.stderr)
        sys.exit(1)
    
    # Update VERSION file
    update_version_file(new_version)
    
    # Sync versions across all files
    if not run_sync_script():
        sys.exit(1)
    
    # Create commit if requested
    if create_commit:
        message = f"chore: bump version to {new_version}"
        if not git_commit(message):
            sys.exit(1)
    
    # Create tag if requested
    if create_tag:
        if not git_tag(new_version):
            sys.exit(1)
    
    # Push if requested
    if push:
        if not git_push(create_commit, create_tag):
            sys.exit(1)
    
    print(f"\n[OK] Version bumped to {new_version}")
    if create_tag:
        print(f"  Tag: v{new_version}")
    if create_commit:
        print(f"  Commit: Created")
    if push:
        print(f"  Remote: Pushed")


if __name__ == "__main__":
    main()

