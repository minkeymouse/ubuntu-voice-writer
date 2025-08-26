#!/bin/bash
# Ubuntu Voice Writer Installation Script - Optimized

set -e

echo "🎤 Ubuntu Voice Writer Installation"
echo "=================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install system dependencies
if [ "$EUID" -eq 0 ]; then
    echo "Installing system dependencies..."
    apt update
    apt install -y xdotool xclip
    echo "✅ System dependencies installed"
else
    echo "⚠️  Not running as root. You may need to install dependencies manually:"
    echo "   sudo apt install xdotool xclip"
fi

# Check dependencies
echo "🔍 Checking dependencies..."
if ! command -v xdotool &> /dev/null; then
    echo "❌ xdotool not found. Please install it: sudo apt install xdotool"
    exit 1
fi

if ! command -v xclip &> /dev/null; then
    echo "❌ xclip not found. Please install it: sudo apt install xclip"
    exit 1
fi

echo "✅ Dependencies verified"

# Make scripts executable
chmod +x voicewriter.py
chmod +x launch.sh
chmod +x stop.py
chmod +x update.sh
chmod +x uninstall.sh

# Create desktop file with proper paths
echo "🔧 Creating desktop integration..."
cat > voicewriter.desktop.tmp << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ubuntu Voice Writer
Name[en]=Ubuntu Voice Writer
Comment=Real-time voice dictation tool for Ubuntu
Comment[en]=Real-time voice dictation tool for Ubuntu
Exec=$SCRIPT_DIR/launch.sh
Icon=$SCRIPT_DIR/icons/voice_writer_icon.png
Terminal=false
StartupNotify=true
Categories=AudioVideo;Audio;Utility;
Keywords=voice;dictation;speech;text;microphone;
GenericName=Voice Dictation Tool
EOF

# Install desktop integration
cp voicewriter.desktop.tmp ~/.local/share/applications/voicewriter.desktop
cp voicewriter.desktop.tmp ~/Desktop/voicewriter.desktop
chmod +x ~/Desktop/voicewriter.desktop
rm voicewriter.desktop.tmp

# Display version
VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
echo ""
echo "🎉 Ubuntu Voice Writer Installation Complete!"
echo "Version: $VERSION"
echo ""
echo "To start Ubuntu Voice Writer:"
echo "  ./launch.sh"
echo ""
echo "Or click the desktop icon!"
echo ""
echo "To stop Ubuntu Voice Writer:"
echo "  ./stop.py"
echo ""
echo "To update Ubuntu Voice Writer:"
echo "  ./update.sh"
echo ""
echo "To uninstall Ubuntu Voice Writer:"
echo "  ./uninstall.sh"
