#!/usr/bin/env python3
"""
VoiceWriter - Simple Voice Dictation Tool
A minimal, browser-based dictation tool that types where your cursor is.
"""

import http.server
import socketserver
import json
import subprocess
import threading
import time
import os
import webbrowser
import gc

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default configuration
        return {
            "server": {"port": 8000, "host": "localhost"},
            "typing": {"timeout": 1.5, "batch_size": 10, "delay": 0.005},
            "browser": {"preferred": "chrome", "fallback": "firefox"},
            "speech": {"language": "en-US", "continuous": True, "interim_results": True},
            "ui": {"theme": "default", "auto_close": True}
        }

# Load configuration
config = load_config()

class VoiceWriterHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.last_processed_text = ""
        self.last_processed_time = 0
        self.min_interval = 0.5  # Minimum time between processing same text
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/stop':
            print("🛑 Stop request received")
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>VoiceWriter Stopped</h1>')
            # Force server shutdown immediately
            def shutdown_server():
                try:
                    self.server.shutdown()
                    print("✅ Server shutdown initiated")
                except Exception as e:
                    print(f"❌ Error shutting down server: {e}")
                    # Force exit if normal shutdown fails
                    os._exit(0)
            threading.Timer(0.5, shutdown_server).start()
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests from the web interface"""
        if self.path == '/type':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                text = data.get('text', '').strip()
                
                if text:
                    # Prevent duplicate processing
                    current_time = time.time()
                    if (text == self.last_processed_text and 
                        current_time - self.last_processed_time < self.min_interval):
                        print(f"🔄 Skipping duplicate text: {text[:50]}...")
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'status': 'skipped', 'message': 'Duplicate text'}).encode())
                        return
                    
                    # Prevent very short or suspicious text
                    if len(text) < 2 or text.count(text[0]) == len(text):
                        print(f"⚠️  Skipping suspicious text: {text}")
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'status': 'skipped', 'message': 'Suspicious text'}).encode())
                        return
                    
                    start_time = time.time()
                    print(f"🎤 {text}")
                    success = self.type_text(text)
                    typing_time = time.time() - start_time
                    if typing_time > 0.5:  # Log slow typing
                        print(f"⏱️  Typing took {typing_time:.2f}s")
                    
                    # Update tracking
                    self.last_processed_text = text
                    self.last_processed_time = current_time
                    
                    # Memory optimization - garbage collection for long texts
                    if len(text) > 100:
                        gc.collect()
                    
                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success' if success else 'error'}).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'No text'}).encode())
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
                except:
                    pass
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def end_headers(self):
        """Add CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def process_text(self, text):
        """Process text to add punctuation and formatting - optimized"""
        if not text or not text.strip():
            return text
        
        # Clean up the text
        text = text.strip()
        
        # Quick check for existing punctuation
        if text.endswith(('.', '!', '?', ':', ';', ',')):
            # Just add space if needed
            if text.endswith('.') and not text.endswith('. '):
                text += ' '
            return text
        
        # Optimized sentence detection
        words = text.split()
        if len(words) <= 2:
            return text  # Too short to be a sentence
        
        # Use set for faster lookups
        sentence_endings = {
            'thank you', 'thanks', 'please', 'okay', 'ok', 'yes', 'no',
            'good', 'great', 'fine', 'sure', 'right', 'correct', 'exactly'
        }
        
        # Check last few words for ending phrases
        text_lower = text.lower()
        ends_with_phrase = any(text_lower.endswith(ending) for ending in sentence_endings)
        
        # Add period if it seems like a complete thought
        if ends_with_phrase or len(words) > 5:
            text += '. '
        elif len(words) > 3:  # Medium length sentences
            text += '. '
        
        return text
    
    def type_text(self, text):
        """Type text using optimized methods with configuration"""
        try:
            # Rate limiting - prevent too rapid typing
            current_time = time.time()
            if hasattr(self, 'last_typing_time') and current_time - self.last_typing_time < 0.1:
                time.sleep(0.1)  # Minimum delay between typing operations
            self.last_typing_time = current_time
            
            # Process text to add punctuation
            processed_text = self.process_text(text)
            
            # Get configuration values
            timeout = config.get('typing', {}).get('timeout', 1.5)
            batch_size = config.get('typing', {}).get('batch_size', 10)
            delay = config.get('typing', {}).get('delay', 0.005)
            
            # Method 1: Direct typing (fastest)
            result = subprocess.run(['xdotool', 'type', processed_text], 
                                  capture_output=True, timeout=timeout)
            if result.returncode == 0:
                return True
            
            # Method 2: Clipboard (more reliable)
            subprocess.run(['xclip', '-selection', 'clipboard'], 
                         input=processed_text.encode(), capture_output=True, timeout=timeout/2)
            time.sleep(delay * 10)  # Slightly longer delay for clipboard
            result = subprocess.run(['xdotool', 'key', 'ctrl+v'], 
                                  capture_output=True, timeout=timeout/2)
            if result.returncode == 0:
                return True
            
            # Method 3: Character by character (most reliable)
            for i in range(0, len(processed_text), batch_size):
                batch = processed_text[i:i+batch_size]
                subprocess.run(['xdotool', 'type', batch], 
                             capture_output=True, timeout=timeout/3)
                time.sleep(delay)
            return True
            
        except Exception as e:
            print(f"❌ Typing failed: {e}")
            return False

def create_html():
    """Create the optimized HTML interface"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>VoiceWriter</title>
    <style>
        body { font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        button { padding: 15px 30px; font-size: 16px; border: none; border-radius: 8px; cursor: pointer; margin: 8px; transition: all 0.3s; }
        .start { background: #4CAF50; color: white; }
        .start:hover { background: #45a049; }
        .stop { background: #f44336; color: white; }
        .stop:hover { background: #da190b; }
        .quit { background: #ff9800; color: white; }
        .quit:hover { background: #f57c00; }
        .status { text-align: center; margin: 20px 0; padding: 15px; border-radius: 8px; font-weight: bold; }
        .ready { background: #e8f5e8; color: #2e7d32; }
        .recording { background: #fff3e0; color: #ef6c00; }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VoiceWriter</h1>
        <div style="text-align: center;">
            <button id="startBtn" class="start">Start Dictation</button>
            <button id="stopBtn" class="stop" disabled>Stop</button>
            <button id="quitBtn" class="quit">Quit</button>
        </div>
        <div id="status" class="status ready">Ready to dictate</div>
    </div>

    <script>
        class VoiceWriter {
            constructor() {
                this.recognition = null;
                this.isRecording = false;
                this.shouldBeRecording = false;
                this.lastSentText = "";
                this.lastSentTime = 0;
                this.initSpeechRecognition();
                this.bindEvents();
            }

            initSpeechRecognition() {
                if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                    this.showError('Speech recognition not supported. Use Chrome or Edge.');
                    return;
                }

                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                this.recognition = new SpeechRecognition();
                
                this.recognition.continuous = false;  // Changed to false to prevent loops
                this.recognition.interimResults = false;  // Changed to false to prevent partial results
                this.recognition.lang = 'en-US';
                
                this.recognition.onstart = () => {
                    this.isRecording = true;
                    this.updateUI();
                    this.showStatus('Recording...', 'recording');
                };
                
                this.recognition.onresult = (event) => {
                    let finalTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript;
                        }
                    }
                    
                    if (finalTranscript) {
                        this.sendToPython(finalTranscript);
                    }
                };
                
                this.recognition.onerror = (event) => {
                    this.showError(`Error: ${event.error}`);
                    this.stopRecording();
                };
                
                this.recognition.onend = () => {
                    this.isRecording = false;
                    this.updateUI();
                    this.showStatus('Ready to dictate', 'ready');
                    
                    // Restart recognition if it was supposed to be recording
                    if (this.shouldBeRecording) {
                        setTimeout(() => {
                            if (this.shouldBeRecording) {
                                this.startRecording();
                            }
                        }, 100);
                    }
                };
            }

            bindEvents() {
                document.getElementById('startBtn').addEventListener('click', () => this.startRecording());
                document.getElementById('stopBtn').addEventListener('click', () => this.stopRecording());
                document.getElementById('quitBtn').addEventListener('click', () => this.quitServer());
            }

            startRecording() {
                if (!this.recognition) return;
                this.shouldBeRecording = true;
                try {
                    this.recognition.start();
                } catch (error) {
                    this.showError('Error starting recognition');
                }
            }

            stopRecording() {
                this.shouldBeRecording = false;
                if (this.recognition && this.isRecording) {
                    this.recognition.stop();
                }
            }

            async sendToPython(text) {
                // Prevent rapid-fire requests
                if (this.lastSentText === text && Date.now() - this.lastSentTime < 500) {
                    console.log('Skipping duplicate text on client side');
                    return;
                }
                
                this.lastSentText = text;
                this.lastSentTime = Date.now();
                
                try {
                    const response = await fetch('/type', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const result = await response.json();
                    if (result.status === 'skipped') {
                        console.log('Server skipped text:', result.message);
                    } else if (result.status !== 'success') {
                        this.showError('Error sending text');
                    }
                } catch (error) {
                    this.showError('Error sending text');
                }
            }

            updateUI() {
                document.getElementById('startBtn').disabled = this.isRecording;
                document.getElementById('stopBtn').disabled = !this.isRecording;
            }

            showStatus(message, type = 'ready') {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = `status ${type}`;
            }

            showError(message) {
                this.showStatus(message, 'error');
            }
            
            quitServer() {
                if (confirm('Quit VoiceWriter?')) {
                    window.location.href = '/stop';
                }
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            new VoiceWriter();
        });
    </script>
</body>
</html>'''
    
    with open('voicewriter.html', 'w') as f:
        f.write(html)

def main():
    """Main function"""
    # Get version
    try:
        with open('VERSION', 'r') as f:
            version = f.read().strip()
    except FileNotFoundError:
        version = "unknown"
    
    print("Ubuntu Voice Writer - Simple Voice Dictation")
    print(f"Version: {version}")
    print("=" * 50)
    
    # Check dependencies
    try:
        subprocess.run(['xdotool', '--version'], capture_output=True, check=True)
        subprocess.run(['xclip', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Missing dependencies. Install with:")
        print("   sudo apt install xdotool xclip")
        return
    
    # Get server configuration
    server_config = config.get('server', {})
    port = server_config.get('port', 8000)
    host = server_config.get('host', 'localhost')
    
    # Check if port is already in use
    try:
        result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print(f"🔄 Port {port} is in use. Stopping existing process...")
            subprocess.run(['pkill', '-f', 'voicewriter.py'], capture_output=True)
            time.sleep(2)  # Wait for process to stop
    except:
        pass
    
    # Create HTML file
    create_html()
    
    # Start server
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", port), VoiceWriterHandler) as httpd:
        print(f"🌐 Server started at http://{host}:{port}")
        print("📱 Opening browser...")
        print("Press Ctrl+C or click Quit to stop")
        print("🔄 Server will auto-close when browser closes")
        
        # Open browser
        browser_process = None
        try:
            webbrowser.open('http://localhost:8000/voicewriter.html')
        except:
            pass
        
        # Start browser monitoring thread - optimized
        def monitor_browser():
            import time
            import psutil
            
            # Track if we've seen any browser connections
            has_seen_connection = False
            consecutive_failures = 0
            
            while True:
                time.sleep(5)  # Increased interval for better performance
                try:
                    # Use more efficient connection check
                    result = subprocess.run(['ss', '-tuln', 'sport = :8000'], 
                                          capture_output=True, text=True, timeout=2)
                    
                    if 'ESTABLISHED' in result.stdout:
                        has_seen_connection = True
                        consecutive_failures = 0
                    elif has_seen_connection and 'ESTABLISHED' not in result.stdout:
                        consecutive_failures += 1
                        if consecutive_failures >= 2:  # Wait for 2 consecutive checks
                            print("🔄 Browser connection lost, shutting down...")
                            httpd.shutdown()
                            break
                        
                except Exception as e:
                    consecutive_failures += 1
                    if consecutive_failures >= 3:  # More lenient for errors
                        print("🔄 Browser monitoring failed, shutting down...")
                        httpd.shutdown()
                        break
        
        browser_thread = threading.Thread(target=monitor_browser, daemon=True)
        browser_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        except Exception as e:
            print(f"\n🛑 Server error: {e}")
        finally:
            print("🧹 Cleaning up...")
            try:
                httpd.shutdown()
                httpd.server_close()
                print("✅ Server cleanup completed")
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")

if __name__ == "__main__":
    main()
