import socket
import threading
import json
import time
import os
from datetime import datetime

class ThreadedNetworkServer:
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.nodes = {}  # {node_id: {info}}
        self.running = True
        self.server_socket = None
        self.ip_pool = self._generate_class_a_ips()
        self.mac_pool = []
        self.total_storage = 2 * 1024 * 1024 * 1024  # 2GB
        self.storage_dir = "distributed_storage"
        
        # Create storage directory
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def _generate_class_a_ips(self):
        """Generate Class A IP addresses (10.0.0.0 to 10.255.255.255)"""
        ips = []
        for i in range(1, 256):
            for j in range(0, 256):
                ips.append(f"10.0.{i}.{j}")
        return ips
    
    def _generate_mac_address(self):
        """Generate a random MAC address"""
        return ':'.join(['%02x' % random.randint(0, 255) for _ in range(6)])
    
    def start(self):
        """Start the threaded network server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            
            print(f"\n{'='*60}")
            print(f"  THREADED NETWORK SERVER")
            print(f"{'='*60}")
            print(f"  Server started on {self.host}:{self.port}")
            print(f"  Total Storage: 2GB")
            print(f"  Storage Directory: {self.storage_dir}")
            print(f"{'='*60}\n")
            
            # Start listener thread
            listener_thread = threading.Thread(target=self._listen_for_nodes)
            listener_thread.daemon = True
            listener_thread.start()
            
            # Start command interface
            self._command_interface()
            
        except Exception as e:
            print(f"Error starting server: {e}")
    
    def _listen_for_nodes(self):
        """Listen for incoming node connections"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, address = self.server_socket.accept()
                thread = threading.Thread(target=self._handle_node, args=(client_socket, address))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def _handle_node(self, client_socket, address):
        """Handle communication with a connected node"""
        try:
            # Receive registration data
            data = client_socket.recv(4096).decode()
            registration = json.loads(data)
            
            node_id = registration['node_id']
            
            # Assign resources
            assigned_ip = self.ip_pool.pop(0) if self.ip_pool else f"10.0.0.{len(self.nodes)}"
            assigned_mac = self._generate_mac_address()
            storage_capacity = self.total_storage // 10  # Divide storage among nodes
            
            # Create node storage directory
            node_storage_path = os.path.join(self.storage_dir, f"node_{node_id}")
            if not os.path.exists(node_storage_path):
                os.makedirs(node_storage_path)
            
            # Store node info
            self.nodes[node_id] = {
                'ip': assigned_ip,
                'mac': assigned_mac,
                'socket': client_socket,
                'address': address,
                'storage_capacity': storage_capacity,
                'storage_path': node_storage_path,
                'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'active'
            }
            
            # Send assignment back to node
            response = {
                'status': 'registered',
                'ip': assigned_ip,
                'mac': assigned_mac,
                'storage_capacity': storage_capacity,
                'storage_path': node_storage_path
            }
            client_socket.send(json.dumps(response).encode())
            
            print(f"\n[REGISTRATION] Node {node_id} registered successfully")
            print(f"  ├─ IP: {assigned_ip}")
            print(f"  ├─ MAC: {assigned_mac}")
            print(f"  └─ Storage: {storage_capacity / (1024*1024):.2f} MB\n")
            
            # Keep connection alive and listen for status updates
            while self.running:
                try:
                    client_socket.settimeout(5.0)
                    msg = client_socket.recv(1024).decode()
                    if not msg:
                        break
                    
                    message = json.loads(msg)
                    if message.get('type') == 'heartbeat':
                        client_socket.send(b'ACK')
                    elif message.get('type') == 'disconnect':
                        break
                        
                except socket.timeout:
                    continue
                except:
                    break
            
            # Node disconnected
            if node_id in self.nodes:
                self.nodes[node_id]['status'] = 'disconnected'
                print(f"\n[DISCONNECTION] Node {node_id} has stopped\n")
                
        except Exception as e:
            print(f"Error handling node: {e}")
        finally:
            client_socket.close()
    
    def _command_interface(self):
        """Command line interface for the server"""
        print("Type 'help' for available commands\n")
        
        while self.running:
            try:
                cmd = input("threaded-network> ").strip().lower()
                
                if cmd == 'quit':
                    self._quit()
                elif cmd == 'nodes':
                    self._show_nodes()
                elif cmd == 'files':
                    self._show_files()
                elif cmd == 'cloud':
                    self._show_cloud()
                elif cmd == 'stats':
                    self._show_stats()
                elif cmd == 'status':
                    self._show_status()
                elif cmd == 'help':
                    self._show_help()
                else:
                    print(f"Unknown command: {cmd}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n")
                self._quit()
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_help(self):
        """Show available commands"""
        print("\n" + "="*60)
        print("  AVAILABLE COMMANDS")
        print("="*60)
        print("  nodes    - Show all registered nodes")
        print("  files    - Show all files in distributed storage")
        print("  cloud    - Show cloud storage overview")
        print("  stats    - Show system statistics")
        print("  status   - Show server status")
        print("  quit     - Shutdown the server")
        print("="*60 + "\n")
    
    def _show_nodes(self):
        """Display all registered nodes"""
        print("\n" + "="*80)
        print(f"  REGISTERED NODES ({len(self.nodes)} total)")
        print("="*80)
        
        if not self.nodes:
            print("  No nodes registered yet.")
        else:
            for node_id, info in self.nodes.items():
                status_symbol = "●" if info['status'] == 'active' else "○"
                print(f"\n  {status_symbol} Node {node_id}")
                print(f"    ├─ IP Address: {info['ip']}")
                print(f"    ├─ MAC Address: {info['mac']}")
                print(f"    ├─ Storage: {info['storage_capacity'] / (1024*1024):.2f} MB")
                print(f"    ├─ Status: {info['status']}")
                print(f"    └─ Connected: {info['connected_at']}")
        
        print("="*80 + "\n")
    
    def _show_files(self):
        """Show all files in distributed storage"""
        print("\n" + "="*80)
        print("  DISTRIBUTED FILES")
        print("="*80)
        
        total_files = 0
        for node_id, info in self.nodes.items():
            storage_path = info['storage_path']
            if os.path.exists(storage_path):
                files = os.listdir(storage_path)
                if files:
                    print(f"\n  Node {node_id} ({info['ip']}):")
                    for f in files:
                        file_path = os.path.join(storage_path, f)
                        size = os.path.getsize(file_path)
                        print(f"    ├─ {f} ({size} bytes)")
                        total_files += 1
        
        if total_files == 0:
            print("  No files in distributed storage yet.")
        
        print(f"\n  Total Files: {total_files}")
        print("="*80 + "\n")
    
    def _show_cloud(self):
        """Show cloud storage overview"""
        print("\n" + "="*80)
        print("  CLOUD STORAGE OVERVIEW")
        print("="*80)
        
        active_nodes = sum(1 for n in self.nodes.values() if n['status'] == 'active')
        total_capacity = sum(n['storage_capacity'] for n in self.nodes.values())
        
        print(f"  Total Capacity: {self.total_storage / (1024*1024*1024):.2f} GB")
        print(f"  Allocated: {total_capacity / (1024*1024):.2f} MB")
        print(f"  Active Nodes: {active_nodes}/{len(self.nodes)}")
        print(f"  Storage Directory: {os.path.abspath(self.storage_dir)}")
        print("="*80 + "\n")
    
    def _show_stats(self):
        """Show system statistics"""
        print("\n" + "="*80)
        print("  SYSTEM STATISTICS")
        print("="*80)
        
        active = sum(1 for n in self.nodes.values() if n['status'] == 'active')
        disconnected = len(self.nodes) - active
        
        print(f"  Total Nodes: {len(self.nodes)}")
        print(f"  Active Nodes: {active}")
        print(f"  Disconnected Nodes: {disconnected}")
        print(f"  Available IPs: {len(self.ip_pool)}")
        print(f"  Server Uptime: Running")
        print("="*80 + "\n")
    
    def _show_status(self):
        """Show server status"""
        print("\n" + "="*80)
        print("  SERVER STATUS")
        print("="*80)
        print(f"  Host: {self.host}")
        print(f"  Port: {self.port}")
        print(f"  Status: Running")
        print(f"  Registered Nodes: {len(self.nodes)}")
        print("="*80 + "\n")
    
    def _quit(self):
        """Shutdown the server"""
        print("\nShutting down server...")
        self.running = False
        
        # Close all node connections
        for node_id, info in self.nodes.items():
            try:
                info['socket'].close()
            except:
                pass
        
        if self.server_socket:
            self.server_socket.close()
        
        print("Server stopped.\n")
        exit(0)

if __name__ == "__main__":
    import random
    server = ThreadedNetworkServer(host='127.0.0.1', port=9000)
    server.start()