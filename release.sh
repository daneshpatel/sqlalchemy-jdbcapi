#!/usr/bin/env sh
# Release script for sqlalchemy-jdbcapi to PyPI

set -e  # Exit on error

VERSION="${1}"

if [ -z "$VERSION" ]; then
    echo "❌ Error: Version number required"
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 2.0.0"
    exit 1
fi

echo "🚀 Releasing sqlalchemy-jdbcapi v${VERSION} to PyPI..."
echo ""

# Verify git status
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working directory is not clean"
    echo "Please commit or stash your changes first"
    git status
    exit 1
fi

# Verify on main or develop branch
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" != "main" && "$BRANCH" != "master" && "$BRANCH" != "develop" ]]; then
    echo "⚠️  Warning: Not on main/master/develop branch (currently on: $BRANCH)"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create git tag
echo "🏷️  Creating git tag v${VERSION}..."
git tag -a "v${VERSION}" -m "Release version ${VERSION}"

# Build the package
echo "🔨 Building package..."
./build.sh

# Ask for confirmation
echo ""
echo "📦 Ready to release:"
echo "  - Version: v${VERSION}"
echo "  - Tag: v${VERSION} (created locally)"
echo "  - Artifacts:"
ls -lh dist/
echo ""
read -p "Upload to PyPI? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Upload to PyPI
    echo "📤 Uploading to PyPI..."
    twine upload dist/*

    # Push git tag
    echo "📌 Pushing git tag to remote..."
    git push origin "v${VERSION}"

    echo ""
    echo "✅ Release complete!"
    echo ""
    echo "🎉 Version ${VERSION} is now live on PyPI!"
    echo "🔗 https://pypi.org/project/sqlalchemy-jdbcapi/${VERSION}/"
    echo ""
    echo "Next steps:"
    echo "  1. Create GitHub release: https://github.com/daneshpatel/sqlalchemy-jdbcapi/releases/new"
    echo "  2. Announce the release"
else
    echo "❌ Release cancelled"
    echo "To delete the local tag: git tag -d v${VERSION}"
    exit 1
fi
