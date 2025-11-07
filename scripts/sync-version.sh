#!/bin/bash

# Sync version between package.json and setup.py
# Usage: ./scripts/sync-version.sh

set -e

if [ ! -f "package.json" ] || [ ! -f "setup.py" ]; then
    echo "Error: package.json and setup.py must exist"
    exit 1
fi

# Get version from package.json
NPM_VERSION=$(node -p "require('./package.json').version")
PYTHON_VERSION=$(grep -oP "version=\"\K[^\"]+" setup.py || echo "")

echo "npm version: ${NPM_VERSION}"
echo "Python version: ${PYTHON_VERSION}"

if [ "$NPM_VERSION" != "$PYTHON_VERSION" ]; then
    echo "Versions don't match. Updating setup.py..."
    
    # Update setup.py version (works on macOS and Linux)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/version=\"[^\"]*\"/version=\"${NPM_VERSION}\"/" setup.py
    else
        # Linux
        sed -i "s/version=\"[^\"]*\"/version=\"${NPM_VERSION}\"/" setup.py
    fi
    
    echo "✅ Updated setup.py to version ${NPM_VERSION}"
    
    # Also update __init__.py if it exists
    if [ -f "ffmcp/__init__.py" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/__version__ = \".*\"/__version__ = \"${NPM_VERSION}\"/" ffmcp/__init__.py
        else
            sed -i "s/__version__ = \".*\"/__version__ = \"${NPM_VERSION}\"/" ffmcp/__init__.py
        fi
        echo "✅ Updated ffmcp/__init__.py to version ${NPM_VERSION}"
    fi
else
    echo "✅ Versions are already in sync"
fi

