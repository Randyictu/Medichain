import socket
import threading
import json
import time
import os
import shutil
import random
from datetime import datetime

class ThreadedNetworkServer:
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.nodes = {}  # {node_id: {info}}
        self.files_registry = {}  # {filename: {size, replicas: [node_ids]}}
        self.running = True
        self.server_socket = None
        self.ip_pool = self._generate_class_a_ips()
        self.mac_pool = []
        self.total_storage = 2 * 1024 * 1024 * 1024  # 2GB
        self.storage_dir = "distributed_storage"
        self.lock = threading.Lock()
        
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
            print(f"  THREADED NETWORK SERVER WITH REPLICATION")
            print(f"{'='*60}")
            print(f"  Server started on {self.host}:{self.port}")
            print(f"  Total Storage: 2GB")
            print(f"  Storage Directory: {self.storage_dir}")
            print(f"  Replication: Enabled")
            print(f"{'='*60}\n")
            
            # Start listener thread
            listener_thread = threading.Thread(target=self._listen_for_nodes)
            listener_thread.daemon = True
            listener_thread.start()
            
            # Start file monitoring thread
            monitor_thread = threading.Thread(target=self._monitor_files)
            monitor_thread.daemon = True
            monitor_thread.start()
            
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
        node_id = None
        is_temp_connection = False
        try:
            # Receive registration data
            data = client_socket.recv(4096).decode()
            message = json.loads(data)
            
            if message.get('type') == 'register':
                node_id = message['node_id']
                
                # Check if this is a temporary connection for replication/sync
                if '_replication' in node_id or '_sync' in node_id:
                    is_temp_connection = True
                    base_node_id = node_id.split('_')[0]
                    
                    # Send a simple acknowledgment
                    response = {'status': 'temp_registered'}
                    client_socket.send(json.dumps(response).encode())
                    
                    # Handle the actual request
                    request_data = client_socket.recv(8192).decode()
                    request = json.loads(request_data.strip())
                    
                    if request.get('type') == 'replicate':
                        filename = request.get('filename')
                        source_node = request.get('node_id')
                        result = self._replicate_file(filename, source_node)
                        response = {'type': 'replicate_response', 'status': 'replicated' if result else 'failed'}
                        client_socket.send(json.dumps(response).encode())
                    
                    elif request.get('type') == 'sync':
                        files_list = self._get_all_files()
                        response = {'files': files_list}
                        client_socket.send(json.dumps(response).encode())
                    
                    # Close temp connection
                    client_socket.close()
                    return
                
                # Regular node registration
                assigned_ip = self.ip_pool.pop(0) if self.ip_pool else f"10.0.0.{len(self.nodes)}"
                assigned_mac = self._generate_mac_address()
                storage_capacity = self.total_storage // 10  # Divide storage among nodes
                
                # Create node storage directory
                node_storage_path = os.path.join(self.storage_dir, f"node_{node_id}")
                if not os.path.exists(node_storage_path):
                    os.makedirs(node_storage_path)
                
                # Store node info
                with self.lock:
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
                
                # Replicate existing files to new node
                self._replicate_to_new_node(node_id)
            
            # Keep connection alive and listen for messages (only for regular nodes)
            while self.running and not is_temp_connection:
                try:
                    client_socket.settimeout(5.0)
                    msg = client_socket.recv(8192).decode()
                    if not msg:
                        break
                    
                    message = json.loads(msg)
                    msg_type = message.get('type')
                    
                    if msg_type == 'heartbeat':
                        response = {'type': 'heartbeat_ack'}
                        client_socket.send(json.dumps(response).encode())
                    
                    elif msg_type == 'disconnect':
                        break
                        
                except socket.timeout:
                    continue
                except:
                    break
            
            # Node disconnected
            if node_id and node_id in self.nodes and not is_temp_connection:
                with self.lock:
                    self.nodes[node_id]['status'] = 'disconnected'
                print(f"\n[DISCONNECTION] Node {node_id} has stopped\n")
                
        except Exception as e:
            print(f"Error handling node: {e}")
        finally:
            if not is_temp_connection:
                client_socket.close()
    
    def _replicate_file(self, filename, source_node_id):
        """Replicate a file from source node to all other active nodes"""
        try:
            source_path = os.path.join(self.storage_dir, f"node_{source_node_id}", filename)
            
            if not os.path.exists(source_path):
                print(f"[ERROR] Source file not found: {filename}")
                return False
            
            file_size = os.path.getsize(source_path)
            replicated_count = 0
            
            print(f"\n[REPLICATION] Starting replication of '{filename}'")
            print(f"  Source: Node {source_node_id}")
            
            with self.lock:
                active_nodes = [nid for nid, info in self.nodes.items() 
                               if info['status'] == 'active' and nid != source_node_id]
            
            for node_id in active_nodes:
                try:
                    dest_path = os.path.join(self.storage_dir, f"node_{node_id}", filename)
                    shutil.copy2(source_path, dest_path)
                    replicated_count += 1
                    print(f"  ├─ Replicated to Node {node_id} ✓")
                except Exception as e:
                    print(f"  ├─ Failed to replicate to Node {node_id}: {e}")
            
            # Update files registry
            with self.lock:
                if filename not in self.files_registry:
                    self.files_registry[filename] = {
                        'size': file_size,
                        'replicas': []
                    }
                
                # Add all nodes that have the file
                all_nodes_with_file = [source_node_id] + active_nodes
                self.files_registry[filename]['replicas'] = all_nodes_with_file
            
            print(f"  └─ Replication complete: {replicated_count + 1}/{len(self.nodes)} nodes\n")
            return True
            
        except Exception as e:
            print(f"[ERROR] Replication failed: {e}")
            return False
    
    def _replicate_to_new_node(self, new_node_id):
        """Replicate all existing files to a newly connected node"""
        if not self.files_registry:
            return
        
        print(f"\n[SYNC] Syncing existing files to Node {new_node_id}")
        
        for filename, info in self.files_registry.items():
            if info['replicas']:
                # Get file from any existing node
                source_node = info['replicas'][0]
                source_path = os.path.join(self.storage_dir, f"node_{source_node}", filename)
                
                if os.path.exists(source_path):
                    try:
                        dest_path = os.path.join(self.storage_dir, f"node_{new_node_id}", filename)
                        shutil.copy2(source_path, dest_path)
                        
                        # Update registry
                        with self.lock:
                            if new_node_id not in info['replicas']:
                                info['replicas'].append(new_node_id)
                        
                        print(f"  ├─ Synced: {filename}")
                    except Exception as e:
                        print(f"  ├─ Failed to sync {filename}: {e}")
        
        print(f"  └─ Sync complete\n")
    
    def _get_all_files(self):
        """Get list of all files across all nodes"""
        files_list = []
        
        with self.lock:
            for filename, info in self.files_registry.items():
                files_list.append({
                    'name': filename,
                    'size': info['size'],
                    'replicas': len(info['replicas'])
                })
        
        return files_list
    
    def _monitor_files(self):
        """Monitor file system for changes"""
        while self.running:
            try:
                time.sleep(5)
                
                with self.lock:
                    # Check each node's storage
                    for node_id, info in self.nodes.items():
                        if info['status'] != 'active':
                            continue
                        
                        storage_path = info['storage_path']
                        if not os.path.exists(storage_path):
                            continue
                        
                        # Check for new files
                        for filename in os.listdir(storage_path):
                            file_path = os.path.join(storage_path, filename)
                            if os.path.isfile(file_path):
                                if filename not in self.files_registry:
                                    # New file detected
                                    file_size = os.path.getsize(file_path)
                                    self.files_registry[filename] = {
                                        'size': file_size,
                                        'replicas': [node_id]
                                    }
                
            except Exception as e:
                pass
    
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
                elif cmd == 'registry':
                    self._show_registry()
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
        print("  registry - Show file replication registry")
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
                        
                        # Check replication status
                        replicas = 0
                        if f in self.files_registry:
                            replicas = len(self.files_registry[f]['replicas'])
                        
                        print(f"    ├─ {f} ({size} bytes) - Replicas: {replicas}")
                        total_files += 1
        
        if total_files == 0:
            print("  No files in distributed storage yet.")
        
        print(f"\n  Total Files: {total_files}")
        print("="*80 + "\n")
    
    def _show_registry(self):
        """Show file replication registry"""
        print("\n" + "="*80)
        print("  FILE REPLICATION REGISTRY")
        print("="*80)
        
        if not self.files_registry:
            print("  No files registered yet.")
        else:
            for filename, info in self.files_registry.items():
                print(f"\n  📄 {filename}")
                print(f"    ├─ Size: {info['size']} bytes")
                print(f"    ├─ Replicas: {len(info['replicas'])}")
                print(f"    └─ Nodes: {', '.join(info['replicas'])}")
        
        print("="*80 + "\n")
    
    def _show_cloud(self):
        """Show cloud storage overview"""
        print("\n" + "="*80)
        print("  CLOUD STORAGE OVERVIEW")
        print("="*80)
        
        active_nodes = sum(1 for n in self.nodes.values() if n['status'] == 'active')
        total_capacity = sum(n['storage_capacity'] for n in self.nodes.values())
        total_files = len(self.files_registry)
        
        print(f"  Total Capacity: {self.total_storage / (1024*1024*1024):.2f} GB")
        print(f"  Allocated: {total_capacity / (1024*1024):.2f} MB")
        print(f"  Active Nodes: {active_nodes}/{len(self.nodes)}")
        print(f"  Total Files: {total_files}")
        print(f"  Replication: Enabled")
        print(f"  Storage Directory: {os.path.abspath(self.storage_dir)}")
        print("="*80 + "\n")
    
    def _show_stats(self):
        """Show system statistics"""
        print("\n" + "="*80)
        print("  SYSTEM STATISTICS")
        print("="*80)
        
        active = sum(1 for n in self.nodes.values() if n['status'] == 'active')
        disconnected = len(self.nodes) - active
        total_files = len(self.files_registry)
        
        # Calculate average replication factor
        avg_replication = 0
        if self.files_registry:
            avg_replication = sum(len(info['replicas']) for info in self.files_registry.values()) / len(self.files_registry)
        
        print(f"  Total Nodes: {len(self.nodes)}")
        print(f"  Active Nodes: {active}")
        print(f"  Disconnected Nodes: {disconnected}")
        print(f"  Total Files: {total_files}")
        print(f"  Average Replication Factor: {avg_replication:.1f}")
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
        print(f"  Replication: Enabled")
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
    server = ThreadedNetworkServer(host='127.0.0.1', port=9000)
    server.start()