# threaded.py
import socket, threading, argparse, time, os, json
from common import to_json, ensure_dir, gen_mac, gen_file_id, CHUNK_SIZE, NODES_FILE, FILES_FILE, load_json_file, save_json_file
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 60000
HEARTBEAT_TIMEOUT = 20  # seconds

def read_json_line(sock):
    buff = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            raise ConnectionError("socket closed")
        if ch == b"\n":
            break
        buff += ch
    return json.loads(buff.decode("utf-8"))

class Server:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, dashboard_port=8000):
        self.host = host
        self.port = port
        self.dashboard_port = dashboard_port
        ensure_dir("data")
        self.nodes = load_json_file(NODES_FILE) or {}
        self.files = load_json_file(FILES_FILE) or {}
        self.lock = threading.Lock()
        self.sock = None

    def persist(self):
        with self.lock:
            save_json_file(NODES_FILE, self.nodes)
            save_json_file(FILES_FILE, self.files)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(200)
        print(f"[server] listening on {self.host}:{self.port}")
        print(f"[server] dashboard at http://127.0.0.1:{self.dashboard_port}/")
        threading.Thread(target=self._accept_loop, daemon=True).start()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
        threading.Thread(target=self._dashboard, daemon=True).start()
        try:
            self._operator_loop()
        finally:
            self.persist()

    def _accept_loop(self):
        while True:
            client, addr = self.sock.accept()
            threading.Thread(target=self._handle_connection, args=(client, addr), daemon=True).start()

    def _cleanup_loop(self):
        while True:
            time.sleep(5)
            now = time.time()
            changed = False
            with self.lock:
                for nid, meta in list(self.nodes.items()):
                    if meta.get("connected") and (now - meta.get("last_seen", 0) > HEARTBEAT_TIMEOUT):
                        print(f"[server] heartbeat timeout for {nid}; marking offline")
                        self.nodes[nid]["connected"] = False
                        changed = True
            if changed:
                self.persist()

    def _handle_connection(self, client, addr):
        node_id = None
        try:
            header = read_json_line(client)
            typ = header.get("type")
            if typ == "register":
                meta = header.get("meta", {})
                node_id = meta.get("node_id")
                node_host = meta.get("host")
                node_port = meta.get("port")
                with self.lock:
                    if node_id not in self.nodes:
                        ip = f"10.0.0.{len(self.nodes)+2}"
                        mac = gen_mac()
                        self.nodes[node_id] = {"host": node_host, "port": node_port, "ip": ip, "mac": mac, "connected": True, "last_seen": time.time()}
                    else:
                        self.nodes[node_id].update({"host": node_host, "port": node_port, "connected": True, "last_seen": time.time()})
                    meta_assigned = {"ip": self.nodes[node_id]["ip"], "mac": self.nodes[node_id]["mac"]}
                client.sendall(to_json({"type":"register_ack", "assigned": meta_assigned}))
                print(f"[server] registered {node_id} @ {node_host}:{node_port} ip={meta_assigned['ip']} mac={meta_assigned['mac']}")
                self.persist()
            else:
                client.close()
                return

            while True:
                hdr = read_json_line(client)
                t = hdr.get("type")
                if t == "heartbeat":
                    with self.lock:
                        if node_id in self.nodes:
                            self.nodes[node_id]["last_seen"] = time.time()
                            self.nodes[node_id]["connected"] = True
                            self.persist()
                elif t == "register_file":
                    fid = hdr["file_id"]; fname = hdr["file_name"]; size = hdr["size"]; chunks = hdr["chunks"]
                    with self.lock:
                        self.files[fid] = {"file_name": fname, "owner": node_id, "size": size, "chunks_total": chunks, "nodes_have": [node_id]}
                    client.sendall(to_json({"type":"register_file_ack", "file_id": fid}))
                    print(f"[server] file registered: {fname} id={fid} owner={node_id}")
                    self.persist()
                elif t == "nodes_list_request":
                    with self.lock:
                        client.sendall(to_json({"type":"nodes_list", "nodes": self.nodes}))
                elif t == "request_peer":
                    target = hdr.get("target")
                    with self.lock:
                        tgt = self.nodes.get(target)
                    if not tgt or not tgt.get("connected"):
                        client.sendall(to_json({"type":"peer_response", "ok": False, "reason": "target offline or unknown"}))
                    else:
                        client.sendall(to_json({"type":"peer_response", "ok": True, "host": tgt["host"], "port": tgt["port"]}))
                elif t == "announce_have_chunk":
                    fid = hdr.get("file_id")
                    seq = hdr.get("seq")
                    with self.lock:
                        if fid in self.files:
                            if node_id not in self.files[fid].get("nodes_have", []):
                                self.files[fid].setdefault("nodes_have", []).append(node_id)
                    client.sendall(to_json({"type":"announce_ack", "file_id": fid, "seq": seq}))
                    self.persist()
                elif t == "disconnect":
                    print(f"[server] node {node_id} requested disconnect")
                    with self.lock:
                        if node_id in self.nodes:
                            self.nodes[node_id]["connected"] = False
                    self.persist()
                    break
                else:
                    pass

        except ConnectionError:
            print(f"[server] connection closed for {node_id}")
            with self.lock:
                if node_id and node_id in self.nodes:
                    self.nodes[node_id]["connected"] = False
                    self.nodes[node_id]["last_seen"] = time.time()
            self.persist()
        except Exception as e:
            print("[server] handler error:", e)
        finally:
            try:
                client.close()
            except:
                pass

    def _operator_loop(self):
        print("server> commands: nodes | files | stats | status <node_id> | quit")
        while True:
            cmd = input("server> ").strip()
            if not cmd:
                continue
            if cmd == "quit":
                print("[server] shutting down")
                self.persist()
                os._exit(0)
            elif cmd == "nodes":
                with self.lock:
                    active = {k:v for k,v in self.nodes.items() if v.get("connected")}
                    if not active:
                        print("No active nodes")
                    for nid, v in active.items():
                        print(f"✅ {nid} | {v['host']}:{v['port']} | IP={v['ip']} MAC={v['mac']}")
            elif cmd == "files":
                with self.lock:
                    if not self.files:
                        print("No files registered")
                    for fid, m in self.files.items():
                        print(f"{fid} -> {m['file_name']} owner={m['owner']} size={m['size']} chunks={m['chunks_total']} nodes={m.get('nodes_have', [])}")
            elif cmd.startswith("status"):
                parts = cmd.split()
                if len(parts) < 2:
                    print("usage: status <node_id>")
                    continue
                nid = parts[1]
                with self.lock:
                    if nid not in self.nodes:
                        print("no such node")
                    else:
                        print(json.dumps(self.nodes[nid], indent=2))
            elif cmd == "stats":
                with self.lock:
                    total_nodes = len(self.nodes)
                    connected = sum(1 for v in self.nodes.values() if v.get("connected"))
                    total_files = len(self.files)
                    print(f"nodes: {connected}/{total_nodes} active, files: {total_files}")
            else:
                print("unknown command")

    def _dashboard(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path == "/":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    html = "<html><head><title>Server Dashboard</title></head><body>"
                    html += "<h1>Server Dashboard</h1>"
                    html += "<ul>"
                    html += "<li><a href='/nodes'>Nodes (JSON)</a></li>"
                    html += "<li><a href='/files'>Files (JSON)</a></li>"
                    html += "</ul>"
                    html += "</body></html>"
                    self.wfile.write(html.encode())
                elif parsed.path == "/nodes":
                    with self.lock:
                        data = json.dumps(self.nodes, indent=2)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(data.encode())
                elif parsed.path == "/files":
                    with self.lock:
                        data = json.dumps(self.files, indent=2)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(data.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
        server = HTTPServer(("0.0.0.0", self.dashboard_port), Handler)
        server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument("--dashboard-port", default=8000, type=int)
    args = parser.parse_args()
    s = Server(host=args.host, port=args.port, dashboard_port=args.dashboard_port)
    s.start()
