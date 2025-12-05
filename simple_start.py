"""
Simple launcher that ONLY starts web_api.py
This ensures the platform shows up immediately
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading

def check_file_exists(filename):
    """Check if required file exists"""
    if not os.path.exists(filename):
        print(f"❌ ERROR: {filename} not found!")
        return False
    return True

def generate_protobuf():
    """Generate protocol buffer files if missing"""
    if os.path.exists('cloudsecurity_pb2.py') and os.path.exists('cloudsecurity_pb2_grpc.py'):
        print("✓ Protocol buffer files found")
        return True
    
    print("📦 Generating protocol buffer files...")
    try:
        cmd = [
            sys.executable, '-m', 'grpc_tools.protoc',
            '-I.', '--python_out=.', '--grpc_python_out=.',
            'cloudsecurity.proto'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Protocol buffers generated successfully")
            return True
        else:
            print(f"❌ Failed to generate protocol buffers: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error generating protocol buffers: {e}")
        print("💡 Try manually: python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto")
        return False

def start_cloud_server():
    """Start cloud.py in background"""
    try:
        print("\n🚀 Starting Cloud Security Server (cloud.py)...")
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                [sys.executable, 'cloud.py'],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, 'cloud.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        time.sleep(3)  # Wait for server to start
        
        if process.poll() is None:
            print("✓ Cloud server started successfully (port 51234)")
            return process
        else:
            print("⚠️ Cloud server may have failed to start")
            return None
    except Exception as e:
        print(f"⚠️ Could not start cloud server: {e}")
        return None

def start_web_api():
    """Start web_api.py - THIS IS THE MAIN INTERFACE"""
    try:
        print("\n🌐 Starting Web API Server (web_api.py)...")
        print("This will serve the web interface on http://localhost:5000")
        
        # Run web_api.py directly in this terminal so we can see output
        subprocess.run([sys.executable, 'web_api.py'])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting web API: {e}")

def open_browser():
    """Open browser after a delay"""
    time.sleep(5)  # Wait for web server to fully start
    print("\n🌐 Opening browser to http://localhost:5000")
    try:
        webbrowser.open('http://localhost:5000')
    except:
        print("⚠️ Could not auto-open browser. Please manually visit: http://localhost:5000")

def main():
    print("\n" + "="*70)
    print("  CLOUDSYNC PRO - SIMPLE LAUNCHER")
    print("="*70)
    print("  This will start the web interface on http://localhost:5000")
    print("="*70 + "\n")
    
    # Check required files
    print("📋 Checking required files...")
    required_files = ['cloud.py', 'web_api.py', 'index.html', 'cloudsecurity.proto', 'utils.py', 'param.py']
    
    all_present = True
    for file in required_files:
        if check_file_exists(file):
            print(f"  ✓ {file}")
        else:
            all_present = False
    
    if not all_present:
        print("\n❌ Missing required files! Please ensure all files are in the same directory.")
        input("\nPress Enter to exit...")
        return
    
    # Generate protocol buffers if needed
    if not generate_protobuf():
        print("\n❌ Failed to generate protocol buffers. Platform cannot start.")
        print("💡 Install grpcio-tools: pip install grpcio-tools")
        input("\nPress Enter to exit...")
        return
    
    print("\n✓ All checks passed!\n")
    
    # Start cloud server in background (optional but recommended)
    cloud_process = start_cloud_server()
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start web API (this will block until Ctrl+C)
    print("\n" + "="*70)
    print("  STARTING WEB INTERFACE")
    print("="*70)
    print("  Web Interface: http://localhost:5000")
    print("  Admin Login: admin@cloudsync.com / AdminSecure123!")
    print("  Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    try:
        start_web_api()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        if cloud_process:
            try:
                cloud_process.terminate()
            except:
                pass
    
    print("\n✓ Shutdown complete\n")

if __name__ == "__main__":
    main()