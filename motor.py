import socket
import os
import struct
from xmlrpc import server

import hash_cache   
import hash_verify
import hashlib

SOCK ='/tmp/av.sock'
PATH_MAX = 4096

# Socket para mostrar la salida e la interfaz

SOCKET_PATH = "/tmp/salidaPython.sock"
cliente = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
cliente.connect(SOCKET_PATH)

def hash_file_with_path(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:          # SIEMPRE binario
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def recv_all(conn, size):
    buf = b''
    while len(buf) < size:
        chunk = conn.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("Cliente desconectado antes de enviar todo el paquete")
        buf += chunk
    return buf


hash_cache.init_hashes_db()
hash_cache.init_instances_db()


# SOCKET ENTRE FANOTIFY Y PYTHON
    
if os.path.exists(SOCK):
    os.remove(SOCK) 
    
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(SOCK)
s.listen()

while True:
    conn, _ = s.accept()
    with conn:
        paquete_format = f"iiQ{PATH_MAX}s"
        paquete_size = struct.calcsize(paquete_format)

        data = recv_all(conn, paquete_size)

        pid, ppid, event, path_bytes = struct.unpack(paquete_format, data)
        path = path_bytes.split(b'\x00', 1)[0].decode(errors="replace")

        if(path != "/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"):
            salida=f"PID={pid} PPID={ppid} Path={path}"
            print(salida)
            cliente.sendall((salida + "\n").encode())

        # Decisión AV
        file_hash = hash_file_with_path(path)
        hash_verify.verify_sha256(path,pid,ppid,event)
        print("DECIDIENDO")
        state = hash_cache.get_state(file_hash)
        print(state)
        if(state == None):
            conn.sendall(b"ALLOW")
        elif state[0] >= 2:
            print("DENEGADO")
            conn.sendall(b"DENY")
        else:
            print("PERMITIDO")
            conn.sendall(b"ALLOW")