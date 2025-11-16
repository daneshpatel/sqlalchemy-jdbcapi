#!/usr/bin/env bash
# Build script for sqlalchemy-jdbcapi

set -e  # Exit on error

echo "🔨 Building sqlalchemy-jdbcapi..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info src/*.egg-info

# Install build dependencies
echo "📦 Installing build tools..."
python3 -m pip install --upgrade build twine

# Build the package
echo "🏗️  Building wheel and source distribution..."
python3 -m build

# Check the build
echo "✅ Checking build artifacts..."
twine check dist/*

echo ""
echo "✅ Build complete!"
echo "📦 Artifacts in dist/:"
ls -lh dist/
echo ""
echo "To test locally:"
echo "  pip install dist/*.whl"
echo ""
echo "To upload to TestPyPI:"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI:"
echo "  twine upload dist/*"
