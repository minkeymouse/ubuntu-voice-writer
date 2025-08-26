#!/bin/bash
# VoiceWriter Launcher Script - Optimized

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if VoiceWriter is already running and stop it
if pgrep -f "voicewriter.py" > /dev/null; then
    echo "🔄 Stopping existing VoiceWriter..."
    pkill -f "voicewriter.py"
    sleep 1
fi

# Check if port 8000 is in use and clean it up
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "🔄 Port 8000 is in use. Stopping existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Run VoiceWriter directly (no virtual environment needed)
python3 voicewriter.py
