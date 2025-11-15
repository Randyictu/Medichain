from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode

network = StorageVirtualNetwork()


network = StorageVirtualNetwork()

node1 = StorageVirtualNode("node1", 4, 16, 500*1024*1024, 1000)
node2 = StorageVirtualNode("node2", 8, 32, 1000*1024*1024, 2000)

network.add_node(node1)
network.add_node(node2)

network.connect_nodes("node1", "node2", 1000)

transfer = network.initiate_file_transfer(
    "node1", "node2", "large_dataset.zip", 100 * 1024 * 1024
)

if transfer:
    print("Transfer initiated:", transfer.file_id)

    while True:
        chunks_done, completed = network.process_file_transfer(
            "node1", "node2", transfer.file_id, chunks_per_step=3
        )
        print(f"Transferred {chunks_done} chunks, completed: {completed}")

        if completed:
            print("Transfer completed successfully!")
            break

    stats = network.get_network_stats()
    print(stats)
