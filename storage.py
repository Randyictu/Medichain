# storage.py
import socket, threading, argparse, time, os, json, mmap
from common import to_json, ensure_dir, gen_file_id, gen_mac, CHUNK_SIZE, load_json_file, save_json_file
import tkinter as tk
from tkinter.filedialog import askopenfilename

# helpers
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

def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed while reading bytes")
        buf += chunk
    return buf

# Virtual disk class
class VirtualDisk:
    def __init__(self, path, size_mb=200):
        self.path = path
        self.size = size_mb * 1024 * 1024
        # create sparse file if missing
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.truncate(self.size)
        self.fd = open(path, "r+b")
        self.mm = mmap.mmap(self.fd.fileno(), self.size)

    def write(self, offset, data):
        if offset + len(data) > self.size:
            raise IOError("Write exceeds virtual disk size")
        self.mm.seek(offset)
        self.mm.write(data)

    def read(self, offset, size):
        if offset + size > self.size:
            size = max(0, self.size - offset)
        self.mm.seek(offset)
        return self.mm.read(size)

    def close(self):
        try:
            self.mm.flush()
            self.mm.close()
        finally:
            self.fd.close()

class NodeStorage:
    def __init__(self, node_id, vdisk_mb=200):
        self.node_id = node_id
        ensure_dir("vdisk")
        self.vdisk_path = os.path.join("vdisk", f"vdisk_{node_id}.vhd")
        self.meta_path = os.path.join("vdisk", f"vdisk_{node_id}.json")
        self.disk = VirtualDisk(self.vdisk_path, size_mb=vdisk_mb)
        self.files = load_json_file(self.meta_path) or {}  # filename -> metadata
        # ensure structure: {"filename": {"file_id":..., "size":..., "chunks_total":...}}
        self._sync_from_meta()

    def _sync_from_meta(self):
        # metadata persisted; nothing to scan on disk
        pass

    def persist_meta(self):
        save_json_file(self.meta_path, self.files)

    def add_local(self, src_path):
        if not os.path.isfile(src_path):
            raise FileNotFoundError("no such file")
        name = os.path.basename(src_path)
        size = os.path.getsize(src_path)
        chunks = (size + CHUNK_SIZE - 1)//CHUNK_SIZE
        fid = gen_file_id(name + str(time.time()))
        # write file into vdisk chunk by chunk
        with open(src_path, "rb") as fr:
            seq = 0
            while True:
                chunk = fr.read(CHUNK_SIZE)
                if not chunk:
                    break
                offset = seq * CHUNK_SIZE
                self.disk.write(offset, chunk)
                seq += 1
        # store file metadata
        self.files[name] = {"file_id": fid, "size": size, "chunks_total": chunks}
        self.persist_meta()
        return name, fid, size, chunks

    def list_files(self):
        return self.files

    def lookup(self, filename_or_id):
        for name, m in self.files.items():
            if filename_or_id == name or filename_or_id == m["file_id"]:
                return name, m
        return None, None

    def read_chunk(self, filename, seq):
        meta = self.files.get(filename)
        if not meta:
            return b""
        offset = seq * CHUNK_SIZE
        # compute chunk size (last chunk may be smaller)
        remaining = meta["size"] - offset
        if remaining <= 0:
            return b""
        size = min(remaining, CHUNK_SIZE)
        return self.disk.read(offset, size)

    def write_chunk_by_name(self, filename, seq, data):
        offset = seq * CHUNK_SIZE
        self.disk.write(offset, data)
        # update metadata size if file not previously present or if writing beyond previous size
        meta = self.files.get(filename)
        if not meta:
            # we don't know total size until p2p_done; store temporary metadata
            self.files[filename] = {"file_id": None, "size": 0, "chunks_total": None}
            meta = self.files[filename]
        # compute new size
        end = offset + len(data)
        if end > meta.get("size", 0):
            meta["size"] = end
        self.persist_meta()

class StorageNode:
    def __init__(self, node_id, server_host, server_port, listen_host="0.0.0.0", listen_port=0, vdisk_mb=200):
        self.node_id = node_id
        self.server_host = server_host
        self.server_port = server_port
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.sock_server = None
        self.listener = None
        self.storage = NodeStorage(node_id, vdisk_mb)
        self.ip = None
        self.mac = gen_mac()
        self.running = True

    def start_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.listen_host, self.listen_port))
        s.listen(5)
        self.listener = s
        self.listen_port = s.getsockname()[1]
        print(f"[node] P2P listener started on {self.listen_host}:{self.listen_port}")
        threading.Thread(target=self._accept_p2p, daemon=True).start()

    def _accept_p2p(self):
        while True:
            client, addr = self.listener.accept()
            threading.Thread(target=self._handle_p2p_incoming, args=(client, addr), daemon=True).start()

    def _handle_p2p_incoming(self, client, addr):
        try:
            hdr = read_json_line(client)
            if hdr.get("type") != "p2p_init":
                client.close(); return
            file_id = hdr["file_id"]; fname = hdr["file_name"]; chunks_total = hdr["chunks_total"]
            # compute received chunks by checking metadata size
            received = set()
            meta = self.storage.files.get(fname)
            if meta:
                have = (meta.get("size", 0) + CHUNK_SIZE - 1)//CHUNK_SIZE
                for i in range(have):
                    received.add(i)
            client.sendall(to_json({"type":"have_chunks", "received": list(received)}))
            # accept chunk headers then raw bytes
            while True:
                header = read_json_line(client)
                if header.get("type") == "chunk":
                    fid = header["file_id"]; seq = header["seq"]; size = header["size"]
                    data = recv_exact(client, size)
                    # write into vdisk
                    self.storage.write_chunk_by_name(fname, seq, data)
                    # announce to coordinator (best-effort)
                    try:
                        self._announce_have_chunk(fid, seq)
                    except:
                        pass
                    client.sendall(to_json({"type":"chunk_ack", "file_id": fid, "seq": seq}))
                elif header.get("type") == "p2p_done":
                    fid = header.get("file_id"); name = header.get("file_name"); total_size = header.get("size")
                    # finalize metadata (update file_id, size, chunks_total)
                    meta = self.storage.files.get(name) or {}
                    meta["file_id"] = fid
                    meta["size"] = total_size
                    meta["chunks_total"] = (total_size + CHUNK_SIZE - 1)//CHUNK_SIZE
                    self.storage.files[name] = meta
                    self.storage.persist_meta()
                    client.sendall(to_json({"type":"p2p_done_ack", "file_id": fid}))
                    break
                else:
                    pass
        except ConnectionError:
            pass
        except Exception as e:
            print("[node] p2p incoming error:", e)
        finally:
            try: client.close()
            except: pass

    def _announce_have_chunk(self, file_id, seq):
        try:
            s = socket.create_connection((self.server_host, self.server_port), timeout=3)
            s.sendall(to_json({"type":"announce_have_chunk", "file_id": file_id, "seq": seq, "node_id": self.node_id}))
            _ = read_json_line(s)
            s.close()
        except:
            pass

    def connect_to_server(self):
        s = socket.create_connection((self.server_host, self.server_port))
        self.sock_server = s
        s.sendall(to_json({"type":"register", "meta": {"node_id": self.node_id, "host": self._local_host_for_server(), "port": self.listen_port}}))
        ack = read_json_line(s)
        if ack.get("type") == "register_ack":
            assigned = ack.get("assigned", {})
            self.ip = assigned.get("ip")
            self.mac = assigned.get("mac", self.mac)
            print(f"[node] registered with server. ip={self.ip} mac={self.mac}")
        threading.Thread(target=self._server_reader, daemon=True).start()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()

    def _local_host_for_server(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self.server_host, self.server_port))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _server_reader(self):
        try:
            while True:
                hdr = read_json_line(self.sock_server)
                t = hdr.get("type")
                if t == "nodes_list":
                    print("[node] nodes list from server:")
                    for nid, info in hdr.get("nodes", {}).items():
                        print(" -", nid, info)
                else:
                    pass
        except Exception:
            pass

    def _heartbeat_loop(self):
        while self.running:
            try:
                self.sock_server.sendall(to_json({"type":"heartbeat"}))
            except:
                break
            time.sleep(5)

    # mini-OS
    def cmd_addfile(self, path_arg=None):
        if path_arg is None:
            root = tk.Tk(); root.withdraw()
            p = askopenfilename()
            root.destroy()
            if not p:
                print("no file chosen"); return
            path_arg = p
        try:
            name, fid, size, chunks = self.storage.add_local(path_arg)
            print(f"[node] added local file {name} id={fid} size={size}")
            try:
                self.sock_server.sendall(to_json({"type":"register_file", "file_id": fid, "file_name": name, "size": size, "chunks": chunks}))
                _ = read_json_line(self.sock_server)
            except Exception as e:
                print("warning: could not register file with server:", e)
        except Exception as e:
            print("addfile error:", e)

    def cmd_list(self):
        files = self.storage.list_files()
        if not files:
            print("no local files")
            return
        for n,m in files.items():
            print(f"{n} id={m.get('file_id')} size={m.get('size')} chunks={m.get('chunks_total')}")

    def cmd_nodes(self):
        try:
            self.sock_server.sendall(to_json({"type":"nodes_list_request"}))
        except Exception as e:
            print("error requesting nodes list:", e)

    def cmd_status(self):
        print(f"node_id: {self.node_id} ip={self.ip} mac={self.mac} listen={self.listen_port}")
        self.cmd_list()

    def cmd_send(self, target_node_id, filename_or_id):
        name, meta = self.storage.lookup(filename_or_id)
        if meta:
            fid = meta["file_id"]; fname = name; chunks_total = meta["chunks_total"]; total_size = meta["size"]
        else:
            print("you can only send files that exist locally"); return
        try:
            self.sock_server.sendall(to_json({"type":"request_peer", "target": target_node_id}))
            resp = read_json_line(self.sock_server)
            if not resp.get("ok"):
                print("server refused: ", resp.get("reason")); return
            peer_host = resp.get("host"); peer_port = resp.get("port")
        except Exception as e:
            print("error contacting server for peer info:", e); return
        try:
            peer = socket.create_connection((peer_host, peer_port), timeout=10)
        except Exception as e:
            print("could not connect to peer:", e); return
        try:
            peer.sendall(to_json({"type":"p2p_init", "file_id": fid, "file_name": fname, "chunks_total": chunks_total}))
            have = read_json_line(peer)
            received = set(have.get("received", []))
            print(f"[node] peer already has {len(received)} chunks; sending missing chunks")
            for seq in range(chunks_total):
                if seq in received: continue
                data = self.storage.read_chunk(fname, seq)
                if not data:
                    print(f"chunk {seq} missing locally; abort"); peer.close(); return
                sent_ok = False
                for attempt in range(3):
                    try:
                        peer.sendall(to_json({"type":"chunk", "file_id": fid, "seq": seq, "size": len(data)}))
                        peer.sendall(data)
                        ack = read_json_line(peer)
                        if ack.get("type") == "chunk_ack" and ack.get("seq") == seq:
                            sent_ok = True; break
                    except Exception as e:
                        print(f"[node] chunk {seq} send attempt {attempt+1} failed: {e}")
                        time.sleep(1)
                if not sent_ok:
                    print(f"[node] failed to send chunk {seq} after retries — aborting"); peer.close(); return
            peer.sendall(to_json({"type":"p2p_done", "file_id": fid, "file_name": fname, "size": total_size}))
            done_ack = read_json_line(peer)
            if done_ack.get("type") == "p2p_done_ack":
                print("[node] p2p transfer complete")
            try:
                self.sock_server.sendall(to_json({"type":"register_file", "file_id": fid, "file_name": fname, "size": total_size, "chunks": chunks_total}))
                _ = read_json_line(self.sock_server)
            except:
                pass
        except Exception as e:
            print("p2p transfer error:", e)
        finally:
            try: peer.close()
            except: pass

    def cmd_quit(self):
        try:
            self.sock_server.sendall(to_json({"type":"disconnect"}))
        except:
            pass
        self.running = False
        try: self.sock_server.close()
        except: pass
        try: self.listener.close()
        except: pass

def run_node(args):
    node = StorageNode(args.node_id, args.server_host, args.server_port, listen_host="0.0.0.0", listen_port=args.listen_port, vdisk_mb=args.vdisk_mb)
    node.start_listener()
    node.connect_to_server()
    print("mini-OS cmds: addfile [path] | list | send <target> <filename_or_id> | nodes | status | quit")
    while node.running:
        try:
            cmdline = input("node> ").strip()
        except EOFError:
            cmdline = "quit"
        if not cmdline:
            continue
        parts = cmdline.split()
        c = parts[0]
        if c == "addfile":
            if len(parts) >= 2:
                node.cmd_addfile(parts[1])
            else:
                node.cmd_addfile(None)
        elif c == "list":
            node.cmd_list()
        elif c == "send" and len(parts) >= 3:
            node.cmd_send(parts[1], parts[2])
        elif c == "nodes":
            node.cmd_nodes()
        elif c == "status":
            node.cmd_status()
        elif c == "quit":
            node.cmd_quit()
            break
        else:
            print("unknown command")
    print("node exiting")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--server-host", default="127.0.0.1")
    parser.add_argument("--server-port", type=int, default=60000)
    parser.add_argument("--listen-port", type=int, default=0)
    parser.add_argument("--vdisk-mb", type=int, default=200)
    args = parser.parse_args()
    run_node(args)
