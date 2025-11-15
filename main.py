from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode

network = StorageVirtualNetwork()

node1 = StorageVirtualNode(
    "node1", 4, 16,
    500 * 1024 * 1024,
    1000,
    "10.0.0.1",
    "AA:BB:CC:DD:EE:01"
)

node2 = StorageVirtualNode(
    "node2", 8, 32,
    1000 * 1024 * 1024,
    2000,
    "10.0.0.2",
    "AA:BB:CC:DD:EE:02"
)

network.add_node(node1)
network.add_node(node2)

network.connect_nodes("node1", "node2", 1000)

transfer = network.initiate_file_transfer(
    "node1",
    "node2",
    "large_dataset.zip",
    100 * 1024 * 1024
)

if transfer:
    print("Transfer started:", transfer.file_id)

chunks_done, completed = network.process_file_transfer(
    "node1", "node2",
    transfer.file_id,
    chunks_per_step=1000
)

print("Chunks:", chunks_done, "Completed:", completed)
print(network.get_network_stats())
