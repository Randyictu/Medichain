# storage_virtual_node.py
from typing import List
from enum import Enum

class TransferStatus(Enum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2

class Chunk:
    def __init__(self, chunk_id: int, size: int):
        self.chunk_id = chunk_id
        self.size = size
        self.status = TransferStatus.PENDING

class FileTransfer:
    def __init__(self, file_id: str, file_name: str, file_size: int, source_node_id: str):
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
        self.source_node_id = source_node_id
        self.status = TransferStatus.PENDING

        CHUNK_SIZE = 1024 * 1024
        num_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

        self.chunks: List[Chunk] = [Chunk(i, CHUNK_SIZE) for i in range(num_chunks)]

# ------------------- NIC LAYER ----------------------
class VirtualNIC:
    def __init__(self, ip_address: str, mac_address: str, bandwidth: int):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.bandwidth = bandwidth  # in bytes per second

    def update_bandwidth(self, new_bw: int):
        self.bandwidth = new_bw

class StorageVirtualNode:
    def __init__(self, node_id: str, cpu_capacity: int, memory_capacity: int,
                 storage_capacity: int, bandwidth: int, ip_address: str, mac_address: str):
        self.node_id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.total_storage = storage_capacity
        self.used_storage = 0

        self.nic = VirtualNIC(ip_address, mac_address, bandwidth)
        self.network_utilization = 0
        self.connections = {}  # ip -> bandwidth
        self.active_transfers = {}

    def add_connection(self, target_ip: str, bandwidth: int):
        self.connections[target_ip] = bandwidth

    def get_ip(self):
        return self.nic.ip_address

    def update_bandwidth(self, new_bw: int):
        self.nic.update_bandwidth(new_bw)

    def initiate_file_transfer(self, file_id: str, file_name: str, file_size: int, source_ip: str):
        if self.used_storage + file_size > self.total_storage:
            return None
        transfer = FileTransfer(file_id, file_name, file_size, source_ip)
        transfer.status = TransferStatus.IN_PROGRESS
        self.active_transfers[file_id] = transfer
        return transfer

    def process_chunk_transfer(self, file_id: str, chunk_id: int, source_ip: str) -> bool:
        if file_id not in self.active_transfers:
            return False
        transfer = self.active_transfers[file_id]
        chunk = transfer.chunks[chunk_id]
        if chunk.status == TransferStatus.COMPLETED:
            return True
        chunk.status = TransferStatus.COMPLETED
        self.used_storage += chunk.size
        self.network_utilization += chunk.size
        if all(c.status == TransferStatus.COMPLETED for c in transfer.chunks):
            transfer.status = TransferStatus.COMPLETED
        return True

    def get_storage_utilization(self):
        return {
            "used": self.used_storage,
            "total": self.total_storage,
            "utilization_percent": (self.used_storage / self.total_storage) * 100
        }
