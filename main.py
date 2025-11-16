from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode

network = StorageVirtualNetwork()

node1 = StorageVirtualNode("node1", 4, 16, 500*1024*1024, 5*1024*1024, "10.0.0.1", "AA:BB:CC:DD:EE:01")  # 5 MB/s
node2 = StorageVirtualNode("node2", 8, 32, 1000*1024*1024, 10*1024*1024, "10.0.0.2", "AA:BB:CC:DD:EE:02")  # 10 MB/s

network.add_node(node1)
network.add_node(node2)

network.connect_nodes("node1", "node2", 5*1024*1024)

# Simulate transfer
network.simulate_file_transfer("node1", "node2", "large_dataset.zip", 20*1024*1024)  # 20 MB
