#!/bin/bash
# VoiceWriter Installation Script - Optimized

set -e

echo "🎤 VoiceWriter Installation"
echo "=========================="

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

# Make scripts executable
chmod +x voicewriter.py
chmod +x launch.sh
chmod +x stop.py

# Install desktop integration
echo "Installing desktop integration..."
cp voicewriter.desktop ~/.local/share/applications/
cp voicewriter.desktop ~/Desktop/
chmod +x ~/Desktop/voicewriter.desktop

echo ""
echo "🎉 VoiceWriter Installation Complete!"
echo ""
echo "To start VoiceWriter:"
echo "  ./launch.sh"
echo ""
echo "Or click the desktop icon!"
echo ""
echo "To stop VoiceWriter:"
echo "  ./stop.py"
