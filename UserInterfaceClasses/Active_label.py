from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal
import time
import threading
import socket
import os

SOCKET_PATH = "/tmp/salidaPython.sock"

# This class creates a label that receives data from the socket. The data comes from
# the motor.py file
class Active_label(QTextEdit):
    data_received = pyqtSignal(str)

    # Builder
    def __init__(self):
        super().__init__()

        # Configuración visual
        self.setReadOnly(True)
        self.setStyleSheet("""
            background-color: #333333;
            color: white;
            margin-bottom:50px;
            margin-top:40px;
        """)

        self.setMinimumHeight(350)
        self.setMinimumWidth(400)

        self.setText("Waiting data from antivirus engine")
        self._placeholder_active = True

        # Conectar señal
        self.data_received.connect(self.reload_text)

        # Hilo socket
        self._running = True
        self.thread = threading.Thread(target=self.leer_data, daemon=True)
        self.thread.start()

    # Read data from socket
    def leer_data(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(SOCKET_PATH)
            server.listen(1)

            while self._running:
                try:
                    conn, _ = server.accept()

                    with conn:
                        while self._running:
                            data = conn.recv(1024)
                            if not data:
                                break

                            texto = data.decode("utf-8")
                            self.data_received.emit(texto)

                except Exception as e:
                    self.data_received.emit(f"\nError: {e}\n")

    # Refresh data from socket
    def reload_text(self, texto):
        if(texto != "/usr/bin/git" and texto != "/usr/bin/bash"):
            self.append(texto)
            time.sleep(0.001)
            
    # Stop label
    def stop(self):
        self._running = False