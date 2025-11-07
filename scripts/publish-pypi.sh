#!/bin/bash

# ffmcp PyPI publish script
# Usage: ./scripts/publish-pypi.sh [patch|minor|major] [--skip-git]

set -e

VERSION_TYPE=${1:-patch}
SKIP_GIT=${2}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Publishing ffmcp to PyPI${NC}"
echo ""

# Check if we're in a git repository
if [ -z "$SKIP_GIT" ] && ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not in a git repository. Skipping git operations.${NC}"
    SKIP_GIT="--skip-git"
fi

# Check for uncommitted changes
if [ -z "$SKIP_GIT" ] && ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ Error: You have uncommitted changes. Please commit or stash them first.${NC}"
    exit 1
fi

# Check if Python venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found. Please create one first.${NC}"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep -oP "version=\"\K[^\"]+" setup.py || echo "")
echo -e "${YELLOW}Current version: ${CURRENT_VERSION}${NC}"

# Bump version in package.json first (if it exists)
if [ -f "package.json" ]; then
    echo -e "${GREEN}Bumping ${VERSION_TYPE} version in package.json...${NC}"
    npm version ${VERSION_TYPE} --no-git-tag-version > /dev/null 2>&1
    
    # Sync versions
    echo -e "${GREEN}Syncing versions...${NC}"
    ./scripts/sync-version.sh > /dev/null 2>&1 || echo -e "${YELLOW}⚠️  Could not sync versions${NC}"
else
    # Manual version bump in setup.py
    echo -e "${YELLOW}⚠️  package.json not found. Please bump version manually in setup.py${NC}"
    exit 1
fi

# Update __init__.py version
NEW_VERSION=$(grep -oP "version=\"\K[^\"]+" setup.py || echo "")
if [ -f "ffmcp/__init__.py" ]; then
    echo -e "${GREEN}Updating __init__.py version...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" ffmcp/__init__.py
    else
        sed -i "s/__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" ffmcp/__init__.py
    fi
fi

echo -e "${GREEN}New version: ${NEW_VERSION}${NC}"
echo ""

# Clean old builds
echo -e "${GREEN}Cleaning old builds...${NC}"
rm -rf build/ dist/ *.egg-info

# Build the package
echo -e "${GREEN}Building package...${NC}"
venv/bin/python3.14 -m build

# Check the package
echo -e "${GREEN}Checking package...${NC}"
venv/bin/python3.14 -m twine check dist/*

echo ""
echo -e "${GREEN}✅ Package built successfully!${NC}"
echo ""

# Check for PyPI credentials
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  PyPI credentials not found in environment variables.${NC}"
    echo -e "${YELLOW}   Set TWINE_USERNAME=__token__ and TWINE_PASSWORD=your_token${NC}"
    echo -e "${YELLOW}   Or run: venv/bin/python3.14 -m twine upload dist/*${NC}"
    echo ""
    echo -e "${GREEN}📦 Package files ready in dist/:${NC}"
    ls -lh dist/
    echo ""
    echo -e "${YELLOW}To publish manually, run:${NC}"
    echo -e "${YELLOW}TWINE_USERNAME=__token__ TWINE_PASSWORD=your_token venv/bin/python3.14 -m twine upload dist/*${NC}"
    exit 0
fi

# Upload to PyPI
echo -e "${GREEN}Uploading to PyPI...${NC}"
venv/bin/python3.14 -m twine upload dist/*
echo -e "${GREEN}✅ Published to PyPI!${NC}"
echo ""

# Git operations
if [ -z "$SKIP_GIT" ]; then
    # Commit version change
    echo -e "${GREEN}Committing version change...${NC}"
    git add package.json setup.py ffmcp/__init__.py
    git commit -m "chore: bump version to ${NEW_VERSION}" || true
    
    # Create git tag
    echo -e "${GREEN}Creating git tag v${NEW_VERSION}...${NC}"
    git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}" || true
    
    # Push to remote
    echo -e "${GREEN}Pushing to remote...${NC}"
    git push origin main || git push origin master || true
    git push origin "v${NEW_VERSION}" || true
    
    echo -e "${GREEN}✅ Git tag created and pushed!${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping git operations${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Successfully published ffmcp@${NEW_VERSION} to PyPI!${NC}"
echo ""
echo "View package: https://pypi.org/project/ffmcp/"

