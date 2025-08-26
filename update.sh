#!/bin/bash
# Ubuntu Voice Writer Update Script

set -e

echo "🔄 Ubuntu Voice Writer Update"
echo "============================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if this is a git repository
if [ ! -d ".git" ]; then
    echo "❌ This is not a git repository. Cannot update."
    echo "Please download the latest version from GitHub:"
    echo "https://github.com/minkeymouse/ubuntu-voice-writer"
    exit 1
fi

# Stop any running instances
echo "🛑 Stopping any running instances..."
if pgrep -f "voicewriter.py" > /dev/null; then
    pkill -f "voicewriter.py"
    sleep 2
fi

# Backup current configuration
if [ -f "config.json" ]; then
    echo "💾 Backing up configuration..."
    cp config.json config.json.backup
fi

# Get current version
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
echo "📋 Current version: $CURRENT_VERSION"

# Pull latest changes
echo "⬇️  Downloading updates..."
git pull origin main

# Get new version
NEW_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
echo "📋 New version: $NEW_VERSION"

# Restore configuration if it was overwritten
if [ -f "config.json.backup" ] && [ ! -f "config.json" ]; then
    echo "🔄 Restoring configuration..."
    mv config.json.backup config.json
fi

# Reinstall desktop integration
echo "🔧 Updating desktop integration..."
./install.sh

echo ""
echo "🎉 Update completed successfully!"
echo "Current version: $NEW_VERSION"
echo ""
echo "To start the updated version:"
echo "  ./launch.sh"
