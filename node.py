import socket
import json
import os
import shutil
import threading
import time
import sys
from datetime import datetime

class DistributedNode:
    def __init__(self, node_id, server_host='127.0.0.1', server_port=9000):
        self.node_id = node_id
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = True
        
        # Node properties (assigned by server)
        self.ip = None
        self.mac = None
        self.storage_capacity = 0
        self.storage_path = None
        self.local_storage_path = f"node_{node_id}_local"
        
        # Network properties
        self.bandwidth = "100 Mbps"
        self.network_host = server_host
        self.network_port = server_port
        
        # Create local storage
        if not os.path.exists(self.local_storage_path):
            os.makedirs(self.local_storage_path)
    
    def connect_to_server(self):
        """Connect and register with the threaded network server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            # Send registration
            registration = {
                'node_id': self.node_id,
                'timestamp': datetime.now().isoformat()
            }
            self.socket.send(json.dumps(registration).encode())
            
            # Receive assignment
            response = self.socket.recv(4096).decode()
            assignment = json.loads(response)
            
            if assignment['status'] == 'registered':
                self.ip = assignment['ip']
                self.mac = assignment['mac']
                self.storage_capacity = assignment['storage_capacity']
                self.storage_path = assignment['storage_path']
                
                print(f"\n{'='*60}")
                print(f"  NODE {self.node_id} - MINI OPERATING SYSTEM")
                print(f"{'='*60}")
                print(f"  Registration: SUCCESS")
                print(f"  IP Address: {self.ip}")
                print(f"  MAC Address: {self.mac}")
                print(f"  Storage Capacity: {self.storage_capacity / (1024*1024):.2f} MB")
                print(f"  Storage Path: {self.storage_path}")
                print(f"  Local Path: {self.local_storage_path}")
                print(f"  Bandwidth: {self.bandwidth}")
                print(f"  Network Host: {self.network_host}")
                print(f"  Network Port: {self.network_port}")
                print(f"{'='*60}\n")
                
                # Start heartbeat thread
                heartbeat_thread = threading.Thread(target=self._send_heartbeat)
                heartbeat_thread.daemon = True
                heartbeat_thread.start()
                
                return True
            else:
                print("Registration failed!")
                return False
                
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def _send_heartbeat(self):
        """Send periodic heartbeat to server"""
        while self.running:
            try:
                message = {'type': 'heartbeat', 'node_id': self.node_id}
                self.socket.send(json.dumps(message).encode())
                time.sleep(10)
            except:
                break
    
    def start(self):
        """Start the node operating system"""
        if not self.connect_to_server():
            print("Failed to connect to server. Exiting...")
            return
        
        print("Type 'help' for available commands\n")
        
        while self.running:
            try:
                cmd = input(f"node-{self.node_id}> ").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command == 'quit' or command == 'exit':
                    self._quit()
                elif command == 'help':
                    self._show_help()
                elif command == 'status':
                    self._show_status()
                elif command == 'addfile':
                    self._add_file(args)
                elif command == 'localfiles':
                    self._show_local_files()
                elif command == 'cloudfiles':
                    self._show_cloud_files()
                elif command == 'upload':
                    self._upload_file(args)
                elif command == 'download':
                    self._download_file(args)
                elif command == 'send':
                    self._send_file(args)
                elif command == 'transfer':
                    self._transfer_file(args)
                elif command == 'bandwidth':
                    self._show_bandwidth()
                elif command == 'network':
                    self._show_network_info()
                elif command == 'storage':
                    self._show_storage_info()
                elif command == 'ls':
                    self._list_directory(args)
                elif command == 'rm':
                    self._remove_file(args)
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n")
                self._quit()
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_help(self):
        """Show available commands"""
        print("\n" + "="*60)
        print("  NODE MINI OPERATING SYSTEM - COMMANDS")
        print("="*60)
        print("  File Operations:")
        print("    addfile <filename> <content>  - Create a new file locally")
        print("    localfiles                    - List local files")
        print("    cloudfiles                    - List files in cloud storage")
        print("    upload <filename>             - Upload file to cloud")
        print("    download <filename>           - Download file from cloud")
        print("    ls [local|cloud]              - List files")
        print("    rm <filename> [local|cloud]   - Remove a file")
        print("\n  Network Operations:")
        print("    send <filename> <target_ip>   - Send file to another node")
        print("    transfer <src> <dst>          - Transfer file between locations")
        print("\n  System Information:")
        print("    status                        - Show node status")
        print("    bandwidth                     - Show bandwidth info")
        print("    network                       - Show network configuration")
        print("    storage                       - Show storage information")
        print("\n  General:")
        print("    help                          - Show this help message")
        print("    quit/exit                     - Disconnect from network")
        print("="*60 + "\n")
    
    def _show_status(self):
        """Show node status"""
        print("\n" + "="*60)
        print(f"  NODE {self.node_id} STATUS")
        print("="*60)
        print(f"  IP Address: {self.ip}")
        print(f"  MAC Address: {self.mac}")
        print(f"  Status: Active")
        print(f"  Connection: Connected to {self.network_host}:{self.network_port}")
        print(f"  Storage Used: {self._get_storage_used():.2f} MB / {self.storage_capacity / (1024*1024):.2f} MB")
        print("="*60 + "\n")
    
    def _get_storage_used(self):
        """Calculate storage used"""
        total_size = 0
        if os.path.exists(self.storage_path):
            for f in os.listdir(self.storage_path):
                file_path = os.path.join(self.storage_path, f)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size / (1024 * 1024)
    
    def _add_file(self, args):
        """Create a new file locally"""
        if len(args) < 2:
            print("Usage: addfile <filename> <content>")
            return
        
        filename = args[0]
        content = ' '.join(args[1:])
        
        file_path = os.path.join(self.local_storage_path, filename)
        
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"File '{filename}' created successfully in local storage")
        except Exception as e:
            print(f"Error creating file: {e}")
    
    def _show_local_files(self):
        """List local files"""
        print("\n" + "="*60)
        print(f"  LOCAL FILES (Node {self.node_id})")
        print("="*60)
        
        if not os.path.exists(self.local_storage_path):
            print("  No local storage directory")
            print("="*60 + "\n")
            return
        
        files = os.listdir(self.local_storage_path)
        
        if not files:
            print("  No files in local storage")
        else:
            for f in files:
                file_path = os.path.join(self.local_storage_path, f)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"  ├─ {f} ({size} bytes)")
        
        print("="*60 + "\n")
    
    def _show_cloud_files(self):
        """List cloud files"""
        print("\n" + "="*60)
        print(f"  CLOUD FILES (Node {self.node_id})")
        print("="*60)
        
        if not os.path.exists(self.storage_path):
            print("  No cloud storage directory")
            print("="*60 + "\n")
            return
        
        files = os.listdir(self.storage_path)
        
        if not files:
            print("  No files in cloud storage")
        else:
            for f in files:
                file_path = os.path.join(self.storage_path, f)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"  ├─ {f} ({size} bytes)")
        
        print("="*60 + "\n")
    
    def _upload_file(self, args):
        """Upload file from local to cloud storage"""
        if len(args) < 1:
            print("Usage: upload <filename>")
            return
        
        filename = args[0]
        local_path = os.path.join(self.local_storage_path, filename)
        cloud_path = os.path.join(self.storage_path, filename)
        
        if not os.path.exists(local_path):
            print(f"File '{filename}' not found in local storage")
            return
        
        try:
            shutil.copy2(local_path, cloud_path)
            print(f"File '{filename}' uploaded to cloud successfully")
        except Exception as e:
            print(f"Error uploading file: {e}")
    
    def _download_file(self, args):
        """Download file from cloud to local storage"""
        if len(args) < 1:
            print("Usage: download <filename>")
            return
        
        filename = args[0]
        cloud_path = os.path.join(self.storage_path, filename)
        local_path = os.path.join(self.local_storage_path, filename)
        
        if not os.path.exists(cloud_path):
            print(f"File '{filename}' not found in cloud storage")
            return
        
        try:
            shutil.copy2(cloud_path, local_path)
            print(f"File '{filename}' downloaded to local storage successfully")
        except Exception as e:
            print(f"Error downloading file: {e}")
    
    def _send_file(self, args):
        """Send file to another node"""
        if len(args) < 2:
            print("Usage: send <filename> <target_ip>")
            return
        
        filename = args[0]
        target_ip = args[1]
        
        print(f"Sending '{filename}' to node at {target_ip}...")
        print("(File transfer simulation - in production, this would use socket communication)")
    
    def _transfer_file(self, args):
        """Transfer file between locations"""
        if len(args) < 2:
            print("Usage: transfer <source> <destination>")
            print("Example: transfer local/file.txt cloud/")
            return
        
        source = args[0]
        destination = args[1]
        
        print(f"Transferring from {source} to {destination}...")
        print("Transfer initiated")
    
    def _show_bandwidth(self):
        """Show bandwidth information"""
        print("\n" + "="*60)
        print(f"  BANDWIDTH INFORMATION")
        print("="*60)
        print(f"  Allocated Bandwidth: {self.bandwidth}")
        print(f"  Current Usage: 12.5 Mbps (simulated)")
        print(f"  Available: 87.5 Mbps")
        print("="*60 + "\n")
    
    def _show_network_info(self):
        """Show network configuration"""
        print("\n" + "="*60)
        print(f"  NETWORK CONFIGURATION")
        print("="*60)
        print(f"  Node IP: {self.ip}")
        print(f"  MAC Address: {self.mac}")
        print(f"  Network Host: {self.network_host}")
        print(f"  Network Port: {self.network_port}")
        print(f"  Bandwidth: {self.bandwidth}")
        print(f"  Status: Connected")
        print("="*60 + "\n")
    
    def _show_storage_info(self):
        """Show storage information"""
        used = self._get_storage_used()
        available = (self.storage_capacity / (1024*1024)) - used
        percentage = (used / (self.storage_capacity / (1024*1024))) * 100 if self.storage_capacity > 0 else 0
        
        print("\n" + "="*60)
        print(f"  STORAGE INFORMATION")
        print("="*60)
        print(f"  Total Capacity: {self.storage_capacity / (1024*1024):.2f} MB")
        print(f"  Used: {used:.2f} MB ({percentage:.1f}%)")
        print(f"  Available: {available:.2f} MB")
        print(f"  Cloud Path: {self.storage_path}")
        print(f"  Local Path: {self.local_storage_path}")
        print("="*60 + "\n")
    
    def _list_directory(self, args):
        """List directory contents"""
        location = args[0] if args else 'local'
        
        if location == 'cloud':
            self._show_cloud_files()
        else:
            self._show_local_files()
    
    def _remove_file(self, args):
        """Remove a file"""
        if len(args) < 1:
            print("Usage: rm <filename> [local|cloud]")
            return
        
        filename = args[0]
        location = args[1] if len(args) > 1 else 'local'
        
        if location == 'cloud':
            file_path = os.path.join(self.storage_path, filename)
        else:
            file_path = os.path.join(self.local_storage_path, filename)
        
        if not os.path.exists(file_path):
            print(f"File '{filename}' not found in {location} storage")
            return
        
        try:
            os.remove(file_path)
            print(f"File '{filename}' removed from {location} storage")
        except Exception as e:
            print(f"Error removing file: {e}")
    
    def _quit(self):
        """Disconnect from network"""
        print("\nDisconnecting from network...")
        self.running = False
        
        try:
            # Notify server of disconnect
            message = {'type': 'disconnect', 'node_id': self.node_id}
            self.socket.send(json.dumps(message).encode())
        except:
            pass
        
        if self.socket:
            self.socket.close()
        
        print(f"Node {self.node_id} stopped.\n")
        exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python node.py <node_id>")
        print("Example: python node.py 1")
        sys.exit(1)
    
    node_id = sys.argv[1]
    node = DistributedNode(node_id)
    node.start()