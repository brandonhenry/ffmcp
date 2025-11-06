#!/usr/bin/env bash
# Quick install script for ffmcp

set -e

echo "🚀 Installing ffmcp..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install in development mode
pip3 install -e .

echo "✅ ffmcp installed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your API keys:"
echo "   ffmcp config -p openai -k YOUR_KEY"
echo "   ffmcp config -p anthropic -k YOUR_KEY"
echo ""
echo "2. Try it out:"
echo "   ffmcp generate 'Hello, world!'"
echo ""
echo "3. See all commands:"
echo "   ffmcp --help"

