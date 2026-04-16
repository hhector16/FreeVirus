from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal
import threading
import socket
import os

SOCKET_PATH = "/tmp/salidaPython.sock"

class Active_label(QTextEdit):
    data_received = pyqtSignal(str)

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
        self.data_received.connect(self.actualizar_texto)

        # Hilo socket
        self._running = True
        self.thread = threading.Thread(target=self.leer_data, daemon=True)
        self.thread.start()

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

    def actualizar_texto(self, texto):
        # Añade texto y hace scroll automático
        self.append(texto)

    def stop(self):
        self._running = False