#!/usr/bin/env python3
"""
Stop VoiceWriter servers - Optimized
"""

import subprocess
import signal
import os

def stop_voicewriter():
    """Stop VoiceWriter servers efficiently"""
    print("🛑 Stopping VoiceWriter...")
    
    stopped_processes = 0
    
    # Kill processes containing 'voicewriter.py'
    try:
        result = subprocess.run(['pkill', '-f', 'voicewriter.py'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ VoiceWriter processes stopped")
            stopped_processes += 1
        else:
            print("ℹ️  No VoiceWriter processes found")
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout stopping VoiceWriter processes")
    except Exception as e:
        print(f"❌ Error stopping VoiceWriter: {e}")
    
    # Kill processes on port 8000
    try:
        result = subprocess.run(['lsof', '-ti:8000'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid and pid.isdigit():
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✅ Stopped process on port 8000 (PID {pid})")
                        stopped_processes += 1
                    except ProcessLookupError:
                        pass  # Process already gone
                    except Exception as e:
                        print(f"⚠️  Could not stop PID {pid}: {e}")
        else:
            print("ℹ️  No processes on port 8000")
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout checking port 8000")
    except Exception as e:
        print(f"❌ Error checking port 8000: {e}")
    
    if stopped_processes > 0:
        print("✅ Server cleanup completed")
    else:
        print("ℹ️  No servers were running")

if __name__ == "__main__":
    stop_voicewriter()
