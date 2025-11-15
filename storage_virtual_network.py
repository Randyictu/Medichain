from typing import Dict, Optional, Tuple
import hashlib
import time
from collections import defaultdict
from storage_virtual_node import StorageVirtualNode, FileTransfer, TransferStatus

class StorageVirtualNetwork:
    def __init__(self):
        self.nodes: Dict[str, StorageVirtualNode] = {}
        self.transfer_operations: Dict[str, Dict[str, FileTransfer]] = defaultdict(dict)

    def add_node(self, node: StorageVirtualNode):
        self.nodes[node.node_id] = node

    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int):
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return False

        ip1 = self.nodes[node1_id].get_ip()
        ip2 = self.nodes[node2_id].get_ip()

        self.nodes[node1_id].add_connection(ip2, bandwidth)
        self.nodes[node2_id].add_connection(ip1, bandwidth)
        return True

    def initiate_file_transfer(self, source_node_id: str, target_node_id: str,
                              file_name: str, file_size: int) -> Optional[FileTransfer]:

        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None

        file_id = hashlib.md5(f"{file_name}-{time.time()}".encode()).hexdigest()

        target_node = self.nodes[target_node_id]

        transfer = target_node.initiate_file_transfer(
            file_id,
            file_name,
            file_size,
            source_ip=self.nodes[source_node_id].get_ip()
        )

        if transfer:
            self.transfer_operations[target_node_id][file_id] = transfer
            return transfer

        return None

    def process_file_transfer(self, source_node_id: str, target_node_id: str,
                              file_id: str, chunks_per_step: int = 1):

        if target_node_id not in self.nodes or source_node_id not in self.nodes:
            return 0, False

        if file_id not in self.transfer_operations[target_node_id]:
            return 0, False

        target_node = self.nodes[target_node_id]
        transfer = self.transfer_operations[target_node_id][file_id]

        chunks_transferred = 0

        for chunk in transfer.chunks:
            if chunk.status != TransferStatus.COMPLETED and chunks_transferred < chunks_per_step:
                ok = target_node.process_chunk_transfer(
                    file_id,
                    chunk.chunk_id,
                    self.nodes[source_node_id].get_ip()
                )
                if not ok:
                    return chunks_transferred, False

                chunks_transferred += 1

        if transfer.status == TransferStatus.COMPLETED:
            del self.transfer_operations[target_node_id][file_id]
            return chunks_transferred, True

        return chunks_transferred, False

    def get_network_stats(self):
        total_bandwidth = sum(n.nic.bandwidth for n in self.nodes.values())
        used_bandwidth = sum(n.network_utilization for n in self.nodes.values())
        total_storage = sum(n.total_storage for n in self.nodes.values())
        used_storage = sum(n.used_storage for n in self.nodes.values())

        return {
            "total_nodes": len(self.nodes),
            "total_bandwidth_bps": total_bandwidth,
            "used_bandwidth_bps": used_bandwidth,
            "bandwidth_utilization": (used_bandwidth / total_bandwidth) * 100,
            "total_storage_bytes": total_storage,
            "used_storage_bytes": used_storage,
            "storage_utilization": (used_storage / total_storage) * 100,
            "active_transfers": sum(len(v) for v in self.transfer_operations.values())
        }
