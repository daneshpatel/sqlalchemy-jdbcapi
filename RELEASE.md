# Release Guide for sqlalchemy-jdbcapi

This guide explains how to release a new version to PyPI.

## Prerequisites

1. **PyPI Account**: Register at https://pypi.org
2. **API Token**: Create at https://pypi.org/manage/account/token/
3. **Configure credentials**:
   ```bash
   # Create/edit ~/.pypirc
   [pypi]
   username = __token__
   password = pypi-<your-token-here>
   ```

4. **Install tools**:
   ```bash
   pip install build twine
   ```

## Release Process

### Method 1: Using Release Script (Recommended)

```bash
# Step 1: Ensure you're on main branch with clean working tree
git checkout main
git pull origin main

# Step 2: Run release script
./release.sh 2.0.0

# The script will:
# - Create git tag
# - Build the package
# - Ask for confirmation
# - Upload to PyPI
# - Push git tag
```

### Method 2: Manual Release

```bash
# Step 1: Create and push git tag
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0

# Step 2: Build the package
./build.sh

# Step 3: Upload to PyPI
twine upload dist/*

# Step 4: Verify on PyPI
# Visit: https://pypi.org/project/sqlalchemy-jdbcapi/
```

## Version Bumping

### Using Bump Script

```bash
# Bump major version (2.0.0 -> 3.0.0)
./bump-version.sh major

# Bump minor version (2.0.0 -> 2.1.0)
./bump-version.sh minor

# Bump patch version (2.0.0 -> 2.0.1)
./bump-version.sh patch

# Then commit and tag
git add -A
git commit -m "chore: Bump version to 2.1.0"
git tag v2.1.0
git push && git push --tags
```

### Manual Version Bump

1. Update `src/sqlalchemy_jdbcapi/_version.py`:
   ```python
   __version__ = version = "2.1.0"
   __version_tuple__ = version_tuple = (2, 1, 0)
   ```

2. Update `CHANGELOG.md`:
   ```markdown
   ## [2.1.0] - 2025-01-15
   ### Added
   - New feature description
   ```

3. Commit and tag:
   ```bash
   git add -A
   git commit -m "chore: Bump version to 2.1.0"
   git tag v2.1.0
   git push && git push --tags
   ```

## Testing Before Release

### Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ sqlalchemy-jdbcapi

# Test the installation
python -c "import sqlalchemy_jdbcapi; print(sqlalchemy_jdbcapi.__version__)"
```

### Local Testing

```bash
# Build and install locally
./build.sh
pip install dist/*.whl

# Run tests
pytest tests/

# Test in a virtual environment
python -m venv test_env
source test_env/bin/activate
pip install dist/*.whl
python -c "from sqlalchemy import create_engine; print('✅ Import successful')"
deactivate
rm -rf test_env
```

## Post-Release Checklist

After releasing to PyPI:

- [ ] Create GitHub Release at https://github.com/daneshpatel/sqlalchemy-jdbcapi/releases/new
  - Use the tag you created (e.g., v2.0.0)
  - Copy changelog entry as release notes
  - Attach wheel and source distribution files

- [ ] Update documentation
  - [ ] Check that docs build correctly
  - [ ] Update version references

- [ ] Announce the release
  - [ ] Twitter/Social media
  - [ ] Reddit (r/Python, r/SQLAlchemy)
  - [ ] Python Weekly newsletter
  - [ ] Dev.to or Medium article

- [ ] Monitor for issues
  - [ ] Check PyPI download stats
  - [ ] Watch for GitHub issues
  - [ ] Monitor CI/CD pipeline

## Troubleshooting

### "Invalid distribution" error
```bash
# Rebuild the package
rm -rf dist/ build/
./build.sh
```

### "File already exists" error on PyPI
- You cannot reupload the same version
- Bump the version and try again

### Import errors after installation
- Check that `src/` layout is properly configured in pyproject.toml
- Verify all `__init__.py` files exist
- Check MANIFEST.in includes all necessary files

### setuptools-scm version issues
```bash
# Ensure you have git tags
git tag v2.0.0

# Force regenerate version file
rm src/sqlalchemy_jdbcapi/_version.py
python -m setuptools_scm
```

## Release Workflow Summary

```
1. Development
   ├── Make changes
   ├── Write tests
   ├── Update docs
   └── Update CHANGELOG.md

2. Pre-release
   ├── Ensure all tests pass
   ├── Clean working tree (git status)
   ├── Update version (_version.py)
   └── Update CHANGELOG.md date

3. Build
   ├── ./build.sh
   └── Verify dist/ contents

4. Test (optional)
   ├── Upload to TestPyPI
   └── Install and test

5. Release
   ├── Create git tag (v2.0.0)
   ├── Upload to PyPI (twine upload)
   └── Push tag to GitHub

6. Post-release
   ├── Create GitHub Release
   ├── Announce
   └── Monitor
```

## Version Strategy

We follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes, incompatible API changes
- **Minor** (2.X.0): New features, backward compatible
- **Patch** (2.0.X): Bug fixes, backward compatible

### Examples:

- `2.0.0` → `2.0.1`: Bug fix (use `./bump-version.sh patch`)
- `2.0.0` → `2.1.0`: New feature (use `./bump-version.sh minor`)
- `2.0.0` → `3.0.0`: Breaking change (use `./bump-version.sh major`)

## Quick Reference Commands

```bash
# Build package
./build.sh

# Bump version
./bump-version.sh [major|minor|patch]

# Release to PyPI
./release.sh 2.0.0

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install locally
pip install dist/*.whl

# Run tests
pytest tests/ -v

# Check package
twine check dist/*
```

## Support

For issues with releasing:
- Check GitHub Issues: https://github.com/daneshpatel/sqlalchemy-jdbcapi/issues
- PyPI Help: https://pypi.org/help/
- Python Packaging Guide: https://packaging.python.org/
