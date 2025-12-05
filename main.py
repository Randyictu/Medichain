"""
Integrated CloudSync Pro System Launcher
Manages cloud.py, threaded.py, node.py, and web_api.py
"""

import subprocess
import sys
import os
import time
import signal
import platform
import webbrowser
import http.server
import socketserver
import threading

class CloudSyncProLauncher:
    def __init__(self):
        self.processes = {}
        self.running = True
        self.web_url = "http://localhost:3000"
        self.api_url = "http://localhost:5000"
        self.web_server = None
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def show_banner(self):
        """Display the system banner"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  CLOUDSYNC PRO - INTEGRATED SYSTEM LAUNCHER")
        print("="*70)
        print("  Cloud Storage | Authentication | Distributed Nodes | AI Assistant")
        print("="*70 + "\n")
    
    def start_web_server(self):
        """Start a simple web server on port 3000 to serve index.html"""
        def run_flask_server():
            from flask import Flask, send_from_directory
            app = Flask(__name__, static_folder='.')
            
            @app.route('/')
            def serve_index():
                return send_from_directory('.', 'index.html')
            
            @app.route('/<path:filename>')
            def serve_static(filename):
                try:
                    return send_from_directory('.', filename)
                except:
                    return send_from_directory('.', 'index.html')
            
            app.run(debug=False, host='0.0.0.0', port=3000, use_reloader=False)
        
        thread = threading.Thread(target=run_flask_server, daemon=True)
        thread.start()
        print("[SUCCESS] Web server started on http://localhost:3000")
        
    
    def start_process(self, name, script, args=[], new_terminal=True):
        """Generic process starter"""
        if name in self.processes and self.processes[name].poll() is None:
            print(f"\n[ERROR] {name} is already running!")
            return False
        
        try:
            print(f"\n[INFO] Starting {name}...")
            
            cmd = [sys.executable, script] + args
            
            if new_terminal:
                if platform.system() == 'Windows':
                    process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    terminals = [
                        ['gnome-terminal', '--'] + cmd,
                        ['xterm', '-e'] + cmd,
                        ['konsole', '-e'] + cmd,
                    ]
                    
                    launched = False
                    for term_cmd in terminals:
                        try:
                            process = subprocess.Popen(term_cmd)
                            launched = True
                            break
                        except FileNotFoundError:
                            continue
                    
                    if not launched:
                        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(2)
            
            if process.poll() is None:
                self.processes[name] = process
                print(f"[SUCCESS] {name} started! PID: {process.pid}")
                return True
            else:
                print(f"[ERROR] {name} failed to start!")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to start {name}: {e}")
            return False
    
    def stop_process(self, name):
        """Generic process stopper"""
        if name not in self.processes:
            print(f"\n[INFO] {name} is not running")
            return
        
        try:
            print(f"\n[INFO] Stopping {name}...")
            process = self.processes[name]
            process.terminate()
            time.sleep(1)
            
            if process.poll() is None:
                process.kill()
            
            del self.processes[name]
            print(f"[SUCCESS] {name} stopped")
            
        except Exception as e:
            print(f"[ERROR] Failed to stop {name}: {e}")
    
    def start_cloud_server(self):
        """Start Cloud Security gRPC Server"""
        return self.start_process("Cloud Security Server", "cloud.py")
    
    def start_threaded_network(self):
        """Start Threaded Network Server"""
        return self.start_process("Threaded Network Server", "threaded.py")
    
    def start_web_api(self):
        """Start Web API Server"""
        return self.start_process("Web API Server", "web_api.py")
    
    def start_storage_node(self):
        """Start a new storage node"""
        node_id = input("\nEnter Node ID (e.g., 1, 2, 3...): ").strip()
        
        if not node_id:
            print("[ERROR] Node ID cannot be empty!")
            return
        
        node_name = f"Node_{node_id}"
        
        if node_name in self.processes and self.processes[node_name].poll() is None:
            print(f"[ERROR] Node {node_id} is already running!")
            return
        
        return self.start_process(node_name, "node.py", [node_id])
    
    def open_web_interface(self):
        """Open web interface in browser"""
        print("\n[INFO] Opening web interface in browser...")
        print(f"[INFO] If browser doesn't open, visit: {self.web_url}")
        
        try:
            webbrowser.open(self.web_url)
            print("[SUCCESS] Web interface opened")
        except Exception as e:
            print(f"[ERROR] Failed to open browser: {e}")
            print(f"[INFO] Please manually visit: {self.web_url}")
    
    def quick_start_all(self):
        """Quick start all essential services"""
        print("\n[INFO] Quick starting all services...")
        
        # Start web server first
        self.start_web_server()
        time.sleep(1)
        
        # Start backend services
        self.start_cloud_server()
        time.sleep(2)
        
        self.start_threaded_network()
        time.sleep(2)
        
        self.start_web_api()
        time.sleep(2)
        
        # Start 6 default nodes
        for i in range(1, 7):
            self.start_process(f"Node_{i}", "node.py", [str(i)])
            time.sleep(1)
        
        print("\n[SUCCESS] All services started!")
        print(f"[INFO] Web interface available at: {self.web_url}")
        print(f"[INFO] API available at: {self.api_url}")
    
    def stop_everything(self):
        """Stop all processes"""
        print("\n[INFO] Stopping all services...")
        
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        if self.web_server:
            self.web_server.shutdown()
        
        print("\n[SUCCESS] All services stopped")
    
    def run(self):
        """Main launcher loop"""
        self.show_banner()
        
        print("Welcome to CloudSync Pro!")
        print("Integrated cloud storage with authentication and AI assistance.\n")
        
        # Check for index.html
        if not os.path.exists('index.html'):
            print("[ERROR] index.html not found!")
            print("[INFO] Please save the provided HTML file as 'index.html' in this directory")
            return
        
        # Ask for quick start - auto-start if not interactive
        if sys.stdin.isatty():
            quick_start = input("Quick start all services? (y/n): ").strip().lower()
        else:
            quick_start = 'y'
            print("Quick start all services? (y/n): y (auto-start)")
        
        if quick_start == 'y':
            self.quick_start_all()
            time.sleep(2)
            self.open_web_interface()
        print("\n[INFO] Press Ctrl+C to stop all services and exit")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupt signal received")
            self.stop_everything()
        
        print("\n" + "="*70)
        print("  Thank you for using CloudSync Pro!")
        print("="*70 + "\n")

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'cloud.py',
        'threaded.py',
        'node.py',
        'web_api.py',
        'utils.py',
        'param.py',
        'cloudsecurity.proto'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print("\n[ERROR] Missing required files:")
        for f in missing:
            print(f"  ❌ {f}")
        print("\n[INFO] Please ensure all files are in the same directory")
        return False
    
    # Check for generated protobuf files
    if not os.path.exists('cloudsecurity_pb2.py') or not os.path.exists('cloudsecurity_pb2_grpc.py'):
        print("\n[WARNING] Protocol buffer files not generated!")
        print("[INFO] Run: python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto")
        return False
    
    # Check for index.html
    if not os.path.exists('index.html'):
        print("\n[WARNING] index.html not found!")
        print("[INFO] Please save the provided HTML interface as 'index.html'")
        return False
    
    print("\n[SUCCESS] All required files found!")
    return True

def main():
    """Main entry point"""
    if not check_requirements():
        print("\n[INFO] Please fix the above issues and try again")
        sys.exit(1)
    
    launcher = CloudSyncProLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
    