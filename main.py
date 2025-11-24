# main.py
import subprocess, time, os
HERE = os.path.dirname(__file__) or "."

def start_server():
    return subprocess.Popen(["python", os.path.join(HERE, "threaded.py"), "--host", "0.0.0.0", "--port", "60000", "--dashboard-port", "8000"])

def start_node(node_id, listen_port):
    return subprocess.Popen(["python", os.path.join(HERE, "storage.py"), "--node-id", node_id, "--server-host", "127.0.0.1", "--server-port", "60000", "--listen-port", str(listen_port)])

if __name__ == "__main__":
    p_server = start_server()
    time.sleep(1)
    procs = []
    for i,port in enumerate(range(6001, 6006), start=1):
        nid = f"node{i}"
        p = start_node(nid, port)
        procs.append(p)
        time.sleep(0.5)
    print("Launched server + 5 nodes. Close this script; processes continue.")
