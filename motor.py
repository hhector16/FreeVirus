import socket
import os
import struct
from xmlrpc import server
import threading
from verify_functions import hash_verify
from verify_functions.check_cpu_consume import monitor_loop
from concurrent.futures import ThreadPoolExecutor
import databases.hash_cache as hash_cache
import hashlib

SOCK ='/tmp/av.sock'
PATH_MAX = 4096

FAN_OPEN = 0x00000020

# Socket para mostrar la salida e la interfaz

SOCKET_PATH = "/tmp/salidaPython.sock"
cliente = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
cliente.connect(SOCKET_PATH)

MAX_WORKERS = min(8, (os.cpu_count() or 2) * 2)

executor = ThreadPoolExecutor(
    max_workers=MAX_WORKERS,
    thread_name_prefix="av-worker"
)

def hash_file_with_path(path):
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:  # SIEMPRE binario
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[ERROR HASH] No se pudo abrir {path}: {e}")
        return None

def recv_all(conn, size):
    buf = b''
    while len(buf) < size:
        chunk = conn.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("Cliente desconectado antes de enviar todo el paquete")
        buf += chunk
    return buf


def handle_client(conn):

    with conn:
        try:
            paquete_format = f"iiQ{PATH_MAX}s"
            paquete_size = struct.calcsize(paquete_format)

            data = recv_all(conn, paquete_size)

            pid, ppid, event, path_bytes = struct.unpack(paquete_format, data)
            path = path_bytes.split(b'\x00', 1)[0].decode(errors="replace")

            if (
                path.endswith("-journal") or
                path.endswith("-wal") or
                "hashes.db" in path or
                "instances.db" in path
            ):
                conn.sendall(b"ALLOW")
                return

            if(path != "/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2" and
               path != "/usr/bin/git" and
               path != "usr/bin/bash"):

                salida = f"PID={pid} PPID={ppid} Path={path}"
                print(salida)

                with cliente_lock:
                    cliente.sendall((salida + "\n").encode())

            if(path in whitelist):
                conn.sendall(b"ALLOW")
                return

            if event & FAN_OPEN:
                conn.sendall(b"ALLOW")
                return

            file_hash = hash_file_with_path(path)

            if file_hash is None:
                conn.sendall(b"ALLOW")
                return

            try:
                if not os.path.exists(path):
                    conn.sendall(b"ALLOW")
                    return

            except Exception as e:
                conn.sendall(b"ALLOW")
                print(e)
                return

            hash_verify.verify_sha256(path, pid, ppid, event)

            state = hash_cache.get_state(file_hash)

            if state is None:
                conn.sendall(b"ALLOW")

            elif state[0] >= 2:

                with cliente_lock:
                    cliente.sendall(f"Blocked file: {path}\n".encode())

                conn.sendall(b"DENY")

            else:
                print("PERMITIDO")
                conn.sendall(b"ALLOW")

        except Exception as e:
            print(f"[ERROR HANDLE CLIENT] {e}")


cliente_lock = threading.Lock()




# SOCKET ENTRE FANOTIFY Y PYTHON
    
if os.path.exists(SOCK):
    os.remove(SOCK) 
    
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(SOCK)
s.listen()

whitelist = ["/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2","/usr/bin/git","usr/bin/bash","/usr/lib/systemd/systemd-executor"]
blacklist = []

threading.Thread(
    target=monitor_loop,
    daemon=True
).start()

while True:
    conn, _ = s.accept()
    executor.submit(handle_client, conn)