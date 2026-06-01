import sys
import requests
import time
import threading

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QFileDialog,
    QHBoxLayout,
    QTextEdit,
    QSizePolicy
)

from PyQt5.QtCore import pyqtSignal, Qt
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

API_KEY = os.getenv("API_KEY")

# This class allows you to analyze a selected file
# It connects to VirusTotal API
class Check_file_screen(QWidget):

    update_text = pyqtSignal(str)

    # Builder
    def __init__(self):
        super().__init__()

        self.file = None

        self.setStyleSheet("background-color: #3d3d3d;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)

        title = QLabel("Check your file")
        title.setStyleSheet(
            "font-size: 24px; color: lightgreen; margin: 60px;"
        )

        p1 = QLabel(
            "In this screen, you will be able to upload a file and "
            "you will receive the virustotal response which will check "
            "if it is a malware or suspicious file"
        )

        p1.setStyleSheet(
            "font-size: 16px; color: darkgray; "
            "margin-left: 40px; margin-right: 40px; "
            "margin-top:20px; margin-bottom:20px"
        )

        p1.setAlignment(Qt.AlignCenter)
        p1.setWordWrap(True)

        container = QWidget()
        container_layout = QHBoxLayout(container)

        self.label = QLabel("No file selected")
        self.label.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed
        )

        self.boton = QPushButton("Select file")
        self.boton.setFixedSize(300, 20)

        self.boton.setStyleSheet(
            "margin-left:70px;margin-right:30px"
        )

        scan_button = QPushButton("Scan file")
        scan_button.setFixedSize(100, 50)

        scan_button.clicked.connect(self.scan_virustotal)

        self.boton.clicked.connect(self.abrir_dialogo)

        p2 = QLabel(
            "Click the Scan button and the result will appear below."
        )

        p2.setStyleSheet(
            "font-size: 16px; color: darkgray; "
            "margin-left: 40px; margin-right: 40px; "
            "margin-top:40px; margin-bottom:60px"
        )

        p2.setAlignment(Qt.AlignCenter)
        p2.setWordWrap(True)

        self.response = QTextEdit()

        self.response.setText(
            "The result will appear here..."
        )

        self.response.setStyleSheet(
            "border: 1px solid black; margin-bottom:20px"
        )

        self.response.setFixedSize(500, 300)

        container_layout.addWidget(self.label)
        container_layout.addWidget(self.boton)
        container_layout.addWidget(scan_button)

        p3 = QLabel(
            "Note: if the results are all 0, "
            "it means that file is not in their database "
            "so its unknown"
        )

        p3.setStyleSheet(
            "font-size: 14px; color: darkgray; "
            "margin-left: 40px; margin-right: 40px; "
            "margin-top:40px; margin-bottom:60px"
        )

        p3.setAlignment(Qt.AlignCenter)
        p3.setWordWrap(True)

        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.setAlignment(Qt.AlignTop)

        self.layout.addWidget(
            title,
            alignment=Qt.AlignHCenter
        )

        self.layout.addWidget(p1)

        self.layout.addWidget(
            container,
            alignment=Qt.AlignHCenter
        )

        self.layout.addWidget(p2)

        self.layout.addWidget(
            self.response,
            alignment=Qt.AlignHCenter
        )

        self.layout.addWidget(p3)

        # conectar signal con la UI
        self.update_text.connect(
            self.response.setText
        )

    # This function opens de file explorer so you select the file
    def abrir_dialogo(self):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select file",
            "",
            "all files (*)"
        )

        if file:
            self.file = file

            self.label.setText(
                f"Selected:\n{file}"
            )

            self.on_file_selected(file)

    # Prints the file selected
    def on_file_selected(self, ruta):
        print("File selected:", ruta)

    # Call to VirusTOtal API
    def scan_virustotal(self):

        path = self.file

        if not path:
            self.response.setText("Invalid file")
            return

        self.response.setText("Uploading file...")

        thread = threading.Thread(
            target=self.scan_worker,
            args=(path,),
            daemon=True
        )

        thread.start()
    
    def scan_worker(self, path):

        try:

            url = "https://www.virustotal.com/api/v3/files"

            headers = {
                "x-apikey": API_KEY
            }

            with open(path, "rb") as f:

                files = {
                    "file": (path, f)
                }

                response = requests.post(
                    url,
                    headers=headers,
                    files=files
                )

            result = response.json()

            print(result)

            analysis_id = result["data"]["id"]

            self.update_text.emit(
                "Analyzing file..."
            )

            report = self.wait_for_analysis(
                analysis_id
            )

            if report is None:

                self.update_text.emit(
                    "Timeout: analysis not completed"
                )

                return

            stats = report["data"]["attributes"]["stats"]

            text = (
                f"Malicious: {stats['malicious']}\n"
                f"Suspicious: {stats['suspicious']}\n"
                f"Undetected: {stats['undetected']}\n"
                f"Harmless: {stats['harmless']}"
            )

            if stats["malicious"] > 0:
                text += "\n\nMalware detected"
            else:
                text += "\n\nFile appears safe"

            self.update_text.emit(text)

        except Exception as e:

            self.update_text.emit(
                f"Error:\n{str(e)}"
            )

    # Gets results
    def get_report(self, analysis_id):

        url = (
            f"https://www.virustotal.com/api/v3/"
            f"analyses/{analysis_id}"
        )

        headers = {
            "x-apikey": API_KEY
        }

        r = requests.get(
            url,
            headers=headers
        )

        return r.json()

    # Waits
    def wait_for_analysis(
        self,
        analysis_id,
        max_attempts=20,
        delay=5
    ):

        for _ in range(max_attempts):

            report = self.get_report(
                analysis_id
            )

            status = report["data"]["attributes"]["status"]

            if status == "completed":
                return report

            time.sleep(delay)

        return None
