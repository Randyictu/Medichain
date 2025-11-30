import subprocess
import sys
import os
import time
import signal
import platform

class IntegratedSystemLauncher:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def show_banner(self):
        """Display the system banner"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  INTEGRATED CLOUD & DISTRIBUTED SYSTEM LAUNCHER")
        print("="*70)
        print("  Cloud Security + Distributed File Storage")
        print("="*70 + "\n")
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "-"*70)
        print("  MAIN MENU")
        print("-"*70)
        print("  CLOUD SECURITY (Authentication & User Management)")
        print("  1. Start Cloud Security Server")
        print("  2. Start Cloud Security Client")
        print("  3. Stop Cloud Security Server")
        print("")
        print("  DISTRIBUTED STORAGE (File System)")
        print("  4. Start Threaded Network Server")
        print("  5. Start Storage Node")
        print("  6. View Running Nodes")
        print("  7. Stop Threaded Network Server")
        print("  8. Stop All Nodes")
        print("")
        print("  SYSTEM MANAGEMENT")
        print("  9. Show System Status")
        print("  10. Stop Everything and Exit")
        print("  0. Exit (keep processes running)")
        print("-"*70)
    
    def start_process(self, name, script, args=[]):
        """Generic process starter"""
        if name in self.processes and self.processes[name].poll() is None:
            print(f"\n[ERROR] {name} is already running!")
            return False
        
        try:
            print(f"\n[INFO] Starting {name}...")
            
            cmd = [sys.executable, script] + args
            
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
            
            time.sleep(1)
            
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
        """Start Cloud Security Server"""
        return self.start_process("Cloud Security Server", "cloud.py")
    
    def start_cloud_client(self):
        """Start Cloud Security Client"""
        return self.start_process("Cloud Security Client", "client.py")
    
    def start_threaded_network(self):
        """Start Threaded Network Server"""
        return self.start_process("Threaded Network Server", "threaded.py")
    
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
    
    def view_nodes(self):
        """View all running nodes"""
        print("\n" + "="*70)
        print("  RUNNING STORAGE NODES")
        print("="*70)
        
        node_processes = {k: v for k, v in self.processes.items() if k.startswith("Node_")}
        
        if not node_processes:
            print("  No storage nodes running")
        else:
            for node_name, process in node_processes.items():
                status = "Running" if process.poll() is None else "Stopped"
                print(f"  ├─ {node_name} - PID: {process.pid} - Status: {status}")
        
        print("="*70)
    
    def stop_all_nodes(self):
        """Stop all storage nodes"""
        node_processes = {k: v for k, v in self.processes.items() if k.startswith("Node_")}
        
        if not node_processes:
            print("\n[INFO] No nodes are running")
            return
        
        print(f"\n[INFO] Stopping {len(node_processes)} node(s)...")
        
        for node_name in list(node_processes.keys()):
            self.stop_process(node_name)
        
        print("[SUCCESS] All nodes stopped")
    
    def show_status(self):
        """Show system status"""
        print("\n" + "="*70)
        print("  SYSTEM STATUS")
        print("="*70)
        
        # Cloud Security Status
        print("\n  CLOUD SECURITY:")
        cloud_server = self.processes.get("Cloud Security Server")
        if cloud_server:
            status = "🟢 Running" if cloud_server.poll() is None else "🔴 Stopped"
            print(f"    ├─ Server: {status} (PID: {cloud_server.pid})")
        else:
            print("    ├─ Server: 🔴 Not Started")
        
        cloud_client = self.processes.get("Cloud Security Client")
        if cloud_client:
            status = "🟢 Running" if cloud_client.poll() is None else "🔴 Stopped"
            print(f"    └─ Client: {status} (PID: {cloud_client.pid})")
        else:
            print("    └─ Client: 🔴 Not Started")
        
        # Distributed Storage Status
        print("\n  DISTRIBUTED STORAGE:")
        threaded_server = self.processes.get("Threaded Network Server")
        if threaded_server:
            status = "🟢 Running" if threaded_server.poll() is None else "🔴 Stopped"
            print(f"    ├─ Server: {status} (PID: {threaded_server.pid})")
        else:
            print("    ├─ Server: 🔴 Not Started")
        
        node_processes = {k: v for k, v in self.processes.items() if k.startswith("Node_")}
        active_nodes = sum(1 for p in node_processes.values() if p.poll() is None)
        print(f"    └─ Nodes: {active_nodes}/{len(node_processes)} Active")
        
        if node_processes:
            for node_name, process in node_processes.items():
                running = process.poll() is None
                status = "🟢" if running else "🔴"
                print(f"        ├─ {status} {node_name} (PID: {process.pid})")
        
        print("="*70)
    
    def stop_everything(self):
        """Stop all processes"""
        print("\n[INFO] Stopping all processes...")
        
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        print("\n[SUCCESS] All processes stopped")
    
    def show_help(self):
        """Show help information"""
        print("\n" + "="*70)
        print("  INTEGRATED SYSTEM HELP")
        print("="*70)
        print("\n  WORKFLOW:")
        print("    1. Start Cloud Security Server (Option 1)")
        print("    2. Start Cloud Security Client (Option 2) - For authentication")
        print("    3. Start Threaded Network Server (Option 4)")
        print("    4. Start Storage Nodes (Option 5) - Create multiple nodes")
        print("    5. Use nodes for distributed file storage")
        print("\n  FEATURES:")
        print("    - User Authentication & Management (Cloud Security)")
        print("    - Two-Factor Authentication with OTP")
        print("    - Distributed File Storage (Threaded Network)")
        print("    - Multiple Storage Nodes with Load Balancing")
        print("    - 2GB Total Distributed Storage")
        print("\n  REQUIREMENTS:")
        print("    - cloud.py, client.py for authentication")
        print("    - threaded.py, node.py for storage")
        print("    - Python 3.7 or higher")
        print("="*70)
    
    def run(self):
        """Main launcher loop"""
        self.show_banner()
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("Welcome to the Integrated Cloud & Distributed System!")
        print("This combines authentication with distributed storage.\n")
        
        while self.running:
            try:
                self.show_menu()
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '1':
                    self.start_cloud_server()
                elif choice == '2':
                    self.start_cloud_client()
                elif choice == '3':
                    self.stop_process("Cloud Security Server")
                elif choice == '4':
                    self.start_threaded_network()
                elif choice == '5':
                    self.start_storage_node()
                elif choice == '6':
                    self.view_nodes()
                elif choice == '7':
                    self.stop_process("Threaded Network Server")
                elif choice == '8':
                    self.stop_all_nodes()
                elif choice == '9':
                    self.show_status()
                elif choice == '10':
                    self.stop_everything()
                    self.running = False
                    print("\n[INFO] Exiting launcher...")
                elif choice == '0':
                    print("\n[INFO] Exiting launcher (processes continue)...")
                    self.running = False
                else:
                    print("\n[ERROR] Invalid choice!")
                
                if self.running and choice in ['1', '2', '3', '4', '5', '7', '8']:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n[INFO] Keyboard interrupt detected")
                confirm = input("Stop all processes and exit? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.stop_everything()
                    self.running = False
            except Exception as e:
                print(f"\n[ERROR] {e}")
                input("\nPress Enter to continue...")
        
        print("\n" + "="*70)
        print("  Thank you for using the Integrated System!")
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
    required_files = ['cloud.py', 'client.py', 'threaded.py', 'node.py']
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print("[ERROR] Missing required files:")
        for f in missing:
            print(f"  - {f}")
        sys.exit(1)
    
    launcher = IntegratedSystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()