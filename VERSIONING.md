# Version Management

This project uses a centralized version management system where the `VERSION` file is the single source of truth for all version numbers across Rust, Python, and related files.

## How It Works

1. **VERSION file**: Contains the current version (e.g., `0.0.1`)
2. **Automatic sync**: Versions are synchronized across:
   - `Cargo.toml` (main Rust crate)
   - `uacalc_lib/Cargo.toml` (Python bindings crate)
   - `pyproject.toml` (Python package)
   - `python/uacalc/__init__.py` (Python package `__version__`)

3. **GitHub Actions**: Automatically syncs versions and creates git tags when `VERSION` changes

## Usage

### Updating the Version

#### Option 1: Manual Update (Recommended)

1. Edit the `VERSION` file with the new version (e.g., `0.0.2`)
2. Commit and push the change:
   ```bash
   git add VERSION
   git commit -m "chore: bump version to 0.0.2"
   git push
   ```
3. The GitHub Action will automatically:
   - Sync versions across all files
   - Create a commit with the synced versions
   - Create a git tag (e.g., `v0.0.2`)
   - Trigger the build-wheels workflow to create a release

#### Option 2: Using the Bump Script

Use the `bump_version.py` script for a more automated workflow:

```bash
# Just update the version (no git operations)
python tools/bump_version.py 0.0.2

# Update version and create a commit
python tools/bump_version.py 0.0.2 --commit

# Update version, create commit, and create tag
python tools/bump_version.py 0.0.2 --tag --commit

# Update version, create commit, create tag, and push everything
python tools/bump_version.py 0.0.2 --tag --commit --push
```

### Checking Version Sync

To verify all versions are in sync without making changes:

```bash
python tools/release.py --check
```

### Manual Version Sync

If you need to manually sync versions (e.g., after editing VERSION file):

```bash
python tools/release.py
```

This will read the `VERSION` file and update all other version files accordingly.

## Version Format

Versions should follow semantic versioning (SemVer) format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples: `0.0.1`, `0.1.0`, `1.0.0`, `1.2.3`

## GitHub Workflow

The `.github/workflows/version-sync.yml` workflow:

- **Triggers**: 
  - Automatically on push to `main`/`master` when `VERSION` file changes
  - Manually via workflow dispatch

- **Actions**:
  1. Reads version from `VERSION` file
  2. Syncs versions across all files
  3. Commits synced versions (if needed)
  4. Creates git tag `v<VERSION>` (if it doesn't exist)
  5. Pushes commits and tags

- **Tag Creation**: 
  - Tags are created as `v<VERSION>` (e.g., `v0.0.1`)
  - Tags trigger the `build-wheels.yml` workflow to build and release Python wheels

## Files Updated

When the version is synced, these files are automatically updated:

1. `VERSION` - Source of truth (you edit this)
2. `Cargo.toml` - Main Rust crate version
3. `uacalc_lib/Cargo.toml` - Python bindings crate version
4. `pyproject.toml` - Python package version
5. `python/uacalc/__init__.py` - Python package `__version__` attribute

## Java Version

Note: The Java version in `org/uacalc/nbui/Version.java` is managed separately and is not automatically synced. This is intentional as the Java codebase has its own versioning scheme (currently `v1.19`).

## Troubleshooting

### Versions are out of sync

Run the sync script:
```bash
python tools/release.py
```

### Tag already exists

If a tag for the version already exists, the workflow will skip tag creation. To create a new release, bump to a new version.

### Check what changed

After syncing, you can see what changed:
```bash
git diff
```

