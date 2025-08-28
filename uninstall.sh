#!/bin/bash
# Ubuntu Voice Writer Uninstall Script

set -e

echo "🗑️  Ubuntu Voice Writer Uninstall"
echo "================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the actual user's home directory (not root's when using sudo)
if [ "$SUDO_USER" ]; then
    USER_HOME=$(eval echo ~$SUDO_USER)
else
    USER_HOME=$HOME
fi

# Stop any running instances
echo "🛑 Stopping any running instances..."
if pgrep -f "voicewriter.py" > /dev/null; then
    pkill -f "voicewriter.py"
    sleep 2
fi

# Remove desktop integration
echo "🗑️  Removing desktop integration..."
rm -f "$USER_HOME/.local/share/applications/voicewriter.desktop"
rm -f "$USER_HOME/Desktop/voicewriter.desktop"

# Remove any generated files
echo "🧹 Cleaning up generated files..."
rm -f "$SCRIPT_DIR/voicewriter.html"

# Remove configuration (optional)
read -p "Remove configuration files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f "$SCRIPT_DIR/config.json"
    echo "✅ Configuration removed"
fi

echo ""
echo "🎉 Ubuntu Voice Writer uninstalled successfully!"
echo ""
echo "Note: System dependencies (xdotool, xclip) were not removed."
echo "To remove them: sudo apt remove xdotool xclip"
