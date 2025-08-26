# Ubuntu Voice Writer

A simple, browser-based voice dictation tool that types where your cursor is.

## Features

- 🎤 **Real-time speech recognition** using your browser's built-in API
- ⌨️ **Automatic typing** into any application where your cursor is
- 🌐 **Browser-based** - works in remote desktop environments
- 🚀 **Fast and reliable** - optimized typing methods
- 🎯 **Simple interface** - just Start, Stop, and Quit buttons
- ⚡ **Lightweight** - no complex dependencies, just system tools
- 🔧 **Configurable** - customizable settings via config.json
- 📦 **Easy updates** - simple update mechanism
- 🗑️ **Clean uninstall** - complete removal process

## Installation

```bash
# Install system dependencies
sudo apt install xdotool xclip

# Run the installation script
./install.sh
```

## Usage

### Start Ubuntu Voice Writer
```bash
./launch.sh
```

Or click the desktop icon!

### How to use
1. **Start** the application (desktop icon or terminal)
2. **Allow microphone access** when prompted
3. **Click "Start Dictation"** to begin recording
4. **Speak clearly** - your speech will be typed automatically
5. **Click "Stop"** to pause dictation
6. **Close the browser tab** or click "Quit" to close the application

## Management

### Update Ubuntu Voice Writer
```bash
./update.sh
```

### Uninstall Ubuntu Voice Writer
```bash
./uninstall.sh
```

### Stop Ubuntu Voice Writer
```bash
./stop.py
```

## Configuration

The application can be customized by editing `config.json`:

```json
{
  "server": {
    "port": 8000,
    "host": "localhost"
  },
  "typing": {
    "timeout": 1.5,
    "batch_size": 10,
    "delay": 0.005
  },
  "browser": {
    "preferred": "chrome",
    "fallback": "firefox"
  },
  "speech": {
    "language": "en-US",
    "continuous": true,
    "interim_results": true
  }
}
```

## How it works

- Uses your browser's Web Speech API (same as Google Voice Typing)
- Sends transcribed text to a Python server
- Python processes text to add punctuation and formatting
- Types processed text using `xdotool` where your cursor is located
- Works in any application (text editors, browsers, terminals, etc.)

## Requirements

- Ubuntu/Linux with desktop environment
- Python 3.6+ (standard library only)
- Chrome or Edge browser
- `xdotool` and `xclip` packages

## Troubleshooting

**Speech recognition not working?**
- Make sure you're using Chrome or Edge
- Allow microphone access when prompted
- Check that your microphone is working

**Typing not working?**
- Make sure `xdotool` and `xclip` are installed
- Try clicking where you want to type first
- Check that the target application accepts text input

**Server won't start?**
- Check if port 8000 is already in use
- Try running `./stop.py` to stop any existing servers

**Desktop icon not working?**
- Run `./install.sh` again to fix desktop integration
- Check that the icon file exists in the icons directory

## Files

- `voicewriter.py` - Main application (single file!)
- `voicewriter.desktop` - Desktop integration
- `install.sh` - Installation script
- `launch.sh` - Launcher script
- `stop.py` - Stop script
- `update.sh` - Update script
- `uninstall.sh` - Uninstall script
- `config.json` - Configuration file
- `VERSION` - Version information
- `icons/` - Application icons
- `README.md` - This documentation

## Performance

- **Typing Speed**: Optimized 3-tier fallback system
- **Memory Usage**: Minimal, with automatic garbage collection
- **CPU Usage**: Efficient browser monitoring
- **Startup Time**: Fast, no complex initialization
- **Configuration**: Loaded at startup for optimal performance

## Version History

- **v1.0.0**: Initial release with basic functionality
- Configuration system
- Update and uninstall scripts
- Improved desktop integration
- Better error handling

That's it! Simple, fast, and focused. 🎤
