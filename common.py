# common.py
import json, uuid, os, random
from typing import Dict

CHUNK_SIZE = 1024 * 1024  # 1 MB
NODES_FILE = "nodes.json"
FILES_FILE = "files.json"

def to_json(msg: Dict) -> bytes:
    return (json.dumps(msg) + "\n").encode("utf-8")

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def gen_file_id(name: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_DNS, name + str(uuid.uuid1())).hex

def gen_mac() -> str:
    parts = [f"{random.randint(0,255):02x}" for _ in range(6)]
    parts[0] = "02"
    return ":".join(parts)

def load_json_file(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
