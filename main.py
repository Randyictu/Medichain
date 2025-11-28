import subprocess
import sys
import os
import time
import signal
import platform

class DistributedSystemLauncher:
    def __init__(self):
        self.processes = []
        self.server_process = None
        self.node_processes = {}
        self.running = True
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def show_banner(self):
        """Display the system banner"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  DISTRIBUTED NETWORK SYSTEM - MAIN LAUNCHER")
        print("="*70)
        print("  A complete distributed system with threaded network and nodes")
        print("="*70 + "\n")
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "-"*70)
        print("  MAIN MENU")
        print("-"*70)
        print("  1. Start Threaded Network Server")
        print("  2. Start a New Node")
        print("  3. View Running Processes")
        print("  4. Stop Server")
        print("  5. Stop a Node")
        print("  6. Stop All Nodes")
        print("  7. Stop Everything and Exit")
        print("  8. Show System Status")
        print("  9. Help")
        print("  0. Exit (keep processes running)")
        print("-"*70)
    
    def start_server(self):
        """Start the threaded network server"""
        if self.server_process:
            print("\n[ERROR] Server is already running!")
            return
        
        try:
            print("\n[INFO] Starting Threaded Network Server...")
            
            if platform.system() == 'Windows':
                # Windows
                self.server_process = subprocess.Popen(
                    [sys.executable, 'threaded_network.py'],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Linux/Mac - try different terminal emulators
                terminals = [
                    ['gnome-terminal', '--', sys.executable, 'threaded_network.py'],
                    ['xterm', '-e', sys.executable, 'threaded_network.py'],
                    ['konsole', '-e', sys.executable, 'threaded_network.py'],
                    ['xfce4-terminal', '-e', f'{sys.executable} threaded_network.py'],
                ]
                
                launched = False
                for term_cmd in terminals:
                    try:
                        self.server_process = subprocess.Popen(term_cmd)
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    # Fallback: run in background
                    print("[WARNING] No terminal emulator found. Running in background...")
                    self.server_process = subprocess.Popen(
                        [sys.executable, 'threaded_network.py'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
            
            time.sleep(2)  # Give server time to start
            
            if self.server_process.poll() is None:
                print(f"[SUCCESS] Server started! PID: {self.server_process.pid}")
            else:
                print("[ERROR] Server failed to start!")
                self.server_process = None
                
        except Exception as e:
            print(f"[ERROR] Failed to start server: {e}")
            self.server_process = None
    
    def start_node(self):
        """Start a new node"""
        if not self.server_process:
            print("\n[ERROR] Please start the server first!")
            return
        
        try:
            node_id = input("\nEnter Node ID (e.g., 1, 2, 3...): ").strip()
            
            if not node_id:
                print("[ERROR] Node ID cannot be empty!")
                return
            
            if node_id in self.node_processes:
                print(f"[ERROR] Node {node_id} is already running!")
                return
            
            print(f"\n[INFO] Starting Node {node_id}...")
            
            if platform.system() == 'Windows':
                # Windows
                process = subprocess.Popen(
                    [sys.executable, 'node.py', node_id],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Linux/Mac
                terminals = [
                    ['gnome-terminal', '--', sys.executable, 'node.py', node_id],
                    ['xterm', '-e', sys.executable, 'node.py', node_id],
                    ['konsole', '-e', sys.executable, 'node.py', node_id],
                    ['xfce4-terminal', '-e', f'{sys.executable} node.py {node_id}'],
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
                    print("[WARNING] No terminal emulator found. Running in background...")
                    process = subprocess.Popen(
                        [sys.executable, 'node.py', node_id],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
            
            time.sleep(1)
            
            if process.poll() is None:
                self.node_processes[node_id] = process
                print(f"[SUCCESS] Node {node_id} started! PID: {process.pid}")
            else:
                print(f"[ERROR] Node {node_id} failed to start!")
                
        except Exception as e:
            print(f"[ERROR] Failed to start node: {e}")
    
    def view_processes(self):
        """View all running processes"""
        print("\n" + "="*70)
        print("  RUNNING PROCESSES")
        print("="*70)
        
        # Check server
        if self.server_process:
            status = "Running" if self.server_process.poll() is None else "Stopped"
            print(f"\n  Server:")
            print(f"    ├─ PID: {self.server_process.pid}")
            print(f"    └─ Status: {status}")
        else:
            print("\n  Server: Not started")
        
        # Check nodes
        if self.node_processes:
            print(f"\n  Nodes ({len(self.node_processes)}):")
            for node_id, process in self.node_processes.items():
                status = "Running" if process.poll() is None else "Stopped"
                print(f"    ├─ Node {node_id} - PID: {process.pid} - Status: {status}")
        else:
            print("\n  Nodes: None started")
        
        print("="*70)
    
    def stop_server(self):
        """Stop the threaded network server"""
        if not self.server_process:
            print("\n[INFO] Server is not running")
            return
        
        try:
            print("\n[INFO] Stopping server...")
            self.server_process.terminate()
            time.sleep(1)
            
            if self.server_process.poll() is None:
                self.server_process.kill()
            
            print("[SUCCESS] Server stopped")
            self.server_process = None
            
        except Exception as e:
            print(f"[ERROR] Failed to stop server: {e}")
    
    def stop_node(self):
        """Stop a specific node"""
        if not self.node_processes:
            print("\n[INFO] No nodes are running")
            return
        
        self.view_processes()
        node_id = input("\nEnter Node ID to stop: ").strip()
        
        if node_id not in self.node_processes:
            print(f"[ERROR] Node {node_id} is not running")
            return
        
        try:
            print(f"\n[INFO] Stopping Node {node_id}...")
            process = self.node_processes[node_id]
            process.terminate()
            time.sleep(1)
            
            if process.poll() is None:
                process.kill()
            
            del self.node_processes[node_id]
            print(f"[SUCCESS] Node {node_id} stopped")
            
        except Exception as e:
            print(f"[ERROR] Failed to stop node: {e}")
    
    def stop_all_nodes(self):
        """Stop all running nodes"""
        if not self.node_processes:
            print("\n[INFO] No nodes are running")
            return
        
        print(f"\n[INFO] Stopping {len(self.node_processes)} node(s)...")
        
        for node_id, process in list(self.node_processes.items()):
            try:
                process.terminate()
                time.sleep(0.5)
                
                if process.poll() is None:
                    process.kill()
                
                print(f"  ├─ Node {node_id} stopped")
                
            except Exception as e:
                print(f"  ├─ Node {node_id} error: {e}")
        
        self.node_processes.clear()
        print("[SUCCESS] All nodes stopped")
    
    def stop_everything(self):
        """Stop all processes"""
        print("\n[INFO] Stopping all processes...")
        
        # Stop all nodes
        if self.node_processes:
            self.stop_all_nodes()
        
        # Stop server
        if self.server_process:
            self.stop_server()
        
        print("\n[SUCCESS] All processes stopped")
    
    def show_status(self):
        """Show system status"""
        print("\n" + "="*70)
        print("  SYSTEM STATUS")
        print("="*70)
        
        # Server status
        if self.server_process:
            server_running = self.server_process.poll() is None
            status = "🟢 Running" if server_running else "🔴 Stopped"
            print(f"\n  Server: {status}")
            if server_running:
                print(f"    ├─ PID: {self.server_process.pid}")
                print(f"    ├─ Host: 127.0.0.1")
                print(f"    └─ Port: 9000")
        else:
            print("\n  Server: 🔴 Not Started")
        
        # Nodes status
        active_nodes = sum(1 for p in self.node_processes.values() if p.poll() is None)
        total_nodes = len(self.node_processes)
        
        print(f"\n  Nodes: {active_nodes}/{total_nodes} Active")
        
        if self.node_processes:
            for node_id, process in self.node_processes.items():
                running = process.poll() is None
                status = "🟢" if running else "🔴"
                print(f"    ├─ {status} Node {node_id} (PID: {process.pid})")
        
        # Storage info
        if os.path.exists('distributed_storage'):
            storage_dirs = [d for d in os.listdir('distributed_storage') 
                          if os.path.isdir(os.path.join('distributed_storage', d))]
            print(f"\n  Storage:")
            print(f"    ├─ Directory: distributed_storage/")
            print(f"    └─ Node Directories: {len(storage_dirs)}")
        
        print("="*70)
    
    def show_help(self):
        """Show help information"""
        print("\n" + "="*70)
        print("  HELP - DISTRIBUTED SYSTEM LAUNCHER")
        print("="*70)
        print("\n  WORKFLOW:")
        print("    1. Start the server first (Option 1)")
        print("    2. Create multiple nodes (Option 2)")
        print("    3. Each node opens in a separate terminal window")
        print("    4. Use node commands in their respective terminals")
        print("    5. Monitor from this launcher or server terminal")
        print("\n  REQUIREMENTS:")
        print("    - threaded_network.py must be in the same directory")
        print("    - node.py must be in the same directory")
        print("    - Python 3.7 or higher")
        print("\n  NODE COMMANDS:")
        print("    Type 'help' in any node terminal to see available commands")
        print("\n  SERVER COMMANDS:")
        print("    Type 'help' in server terminal to see available commands")
        print("\n  TIPS:")
        print("    - Always start the server before creating nodes")
        print("    - Each node needs a unique ID (1, 2, 3, etc.)")
        print("    - You can create 5+ nodes simultaneously")
        print("    - Storage is distributed across all nodes (2GB total)")
        print("\n  TROUBLESHOOTING:")
        print("    - If terminals don't open, check terminal emulator installation")
        print("    - On Windows, use Command Prompt or PowerShell")
        print("    - On Linux, ensure gnome-terminal, xterm, or konsole is installed")
        print("="*70)
    
    def run(self):
        """Main launcher loop"""
        self.show_banner()
        
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("Welcome to the Distributed System Launcher!")
        print("This tool helps you manage the server and nodes easily.\n")
        
        while self.running:
            try:
                self.show_menu()
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '1':
                    self.start_server()
                elif choice == '2':
                    self.start_node()
                elif choice == '3':
                    self.view_processes()
                elif choice == '4':
                    self.stop_server()
                elif choice == '5':
                    self.stop_node()
                elif choice == '6':
                    self.stop_all_nodes()
                elif choice == '7':
                    self.stop_everything()
                    self.running = False
                    print("\n[INFO] Exiting launcher...")
                elif choice == '8':
                    self.show_status()
                elif choice == '9':
                    self.show_help()
                elif choice == '0':
                    print("\n[INFO] Exiting launcher (processes will continue running)...")
                    self.running = False
                else:
                    print("\n[ERROR] Invalid choice! Please try again.")
                
                if self.running and choice in ['1', '2', '4', '5', '6']:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n[INFO] Keyboard interrupt detected")
                confirm = input("Stop all processes and exit? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.stop_everything()
                    self.running = False
            except Exception as e:
                print(f"\n[ERROR] An error occurred: {e}")
                input("\nPress Enter to continue...")
        
        print("\n" + "="*70)
        print("  Thank you for using the Distributed System Launcher!")
        print("="*70 + "\n")
    
    def signal_handler(self, sig, frame):
        """Handle SIGINT signal"""
        print("\n\n[INFO] Interrupt signal received")
        confirm = input("Stop all processes and exit? (y/n): ").strip().lower()
        if confirm == 'y':
            self.stop_everything()
            sys.exit(0)

def main():
    """Main entry point"""
    # Check if required files exist
    if not os.path.exists('threaded.py'):
        print("[ERROR] threaded.py not found in current directory!")
        sys.exit(1)
    
    if not os.path.exists('node.py'):
        print("[ERROR] node.py not found in current directory!")
        sys.exit(1)
    
    launcher = DistributedSystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()