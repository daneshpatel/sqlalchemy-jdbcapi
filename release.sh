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

echo "🚀 Releasing sqlalchemy-jdbcapi ${VERSION} to PyPI..."
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
case "$BRANCH" in
    main|master|develop) : ;;
    *)
        echo "⚠️  Warning: Not on main/master/develop branch (currently on: $BRANCH)"
        printf "Continue anyway? (y/N) "
        IFS= read -r REPLY
        case "$REPLY" in
            [Yy]*) ;;
            *) exit 1 ;;
        esac
        ;;
esac

# Create git tag
echo "🏷️  Creating git tag ${VERSION}..."
git tag -a "${VERSION}" -m "Release version ${VERSION}"

# Build the package
echo "🔨 Building package..."
./build.sh

# Ask for confirmation
echo ""
echo "📦 Ready to release:"
echo "  - Version: ${VERSION}"
echo "  - Tag: ${VERSION} (created locally)"
echo "  - Artifacts:"
ls -lh dist/
echo ""
printf "Upload to PyPI? (y/N) "
IFS= read -r REPLY

case "$REPLY" in
    [Yy]*)
        # Upload to PyPI
        echo "📤 Uploading to PyPI..."
        twine upload dist/*

        # Push git tag
        echo "📌 Pushing git tag to remote..."
        git push origin "${VERSION}"

        echo ""
        echo "✅ Release complete!"
        echo ""
        echo "🎉 Version ${VERSION} is now live on PyPI!"
        echo "🔗 https://pypi.org/project/sqlalchemy-jdbcapi/${VERSION}/"
        echo ""
        echo "Next steps:"
        echo "  1. Create GitHub release: https://github.com/daneshpatel/sqlalchemy-jdbcapi/releases/new"
        echo "  2. Announce the release"
        ;;
    *)
        echo "❌ Release cancelled"
        echo "To delete the local tag: git tag -d ${VERSION}"
        exit 1
        ;;
esac
