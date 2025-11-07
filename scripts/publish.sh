#!/bin/bash

# ffmcp npm publish script
# Usage: ./scripts/publish.sh [patch|minor|major] [--skip-git]

set -e

VERSION_TYPE=${1:-patch}
SKIP_GIT=${2}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Publishing ffmcp to npm${NC}"
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

# Check if logged in to npm
if ! npm whoami > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not logged in to npm. Run 'npm login' first.${NC}"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo -e "${YELLOW}Current version: ${CURRENT_VERSION}${NC}"

# Bump version
echo -e "${GREEN}Bumping ${VERSION_TYPE} version...${NC}"
npm version ${VERSION_TYPE} --no-git-tag-version

# Get new version
NEW_VERSION=$(node -p "require('./package.json').version")
echo -e "${GREEN}New version: ${NEW_VERSION}${NC}"

# Sync Python version if setup.py exists
if [ -f "setup.py" ]; then
    echo -e "${GREEN}Syncing Python version...${NC}"
    ./scripts/sync-version.sh > /dev/null 2>&1 || echo -e "${YELLOW}⚠️  Could not sync Python version${NC}"
fi

echo ""

# Run tests (if they exist)
if npm run test > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  No tests to run${NC}"
fi

# Dry run to see what will be published
echo -e "${GREEN}Checking what will be published...${NC}"
npm pack --dry-run > /dev/null
echo -e "${GREEN}✅ Package check passed${NC}"
echo ""

# Publish to npm
echo -e "${GREEN}Publishing to npm...${NC}"
npm publish
echo -e "${GREEN}✅ Published to npm!${NC}"
echo ""

# Git operations
if [ -z "$SKIP_GIT" ]; then
    # Commit version change
    echo -e "${GREEN}Committing version change...${NC}"
    git add package.json
    [ -f "setup.py" ] && git add setup.py || true
    git commit -m "chore: bump version to ${NEW_VERSION}" || true
    
    # Create git tag
    echo -e "${GREEN}Creating git tag v${NEW_VERSION}...${NC}"
    git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
    
    # Push to remote
    echo -e "${GREEN}Pushing to remote...${NC}"
    git push origin main || git push origin master
    git push origin "v${NEW_VERSION}"
    
    echo -e "${GREEN}✅ Git tag created and pushed!${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping git operations${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Successfully published ffmcp@${NEW_VERSION} to npm!${NC}"
echo ""
echo "View package: https://www.npmjs.com/package/ffmcp"

