from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import sqlite3
class HashTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(900)
        self.setFrameStyle(0)  
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # quitar scroll horizontal   
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)    # scroll vertical solo si hace falta
        self.databaseName = "hashes.db"

        data = self.getData()

        self.setColumnCount(5)
        self.setRowCount(len(data))

        self.setHorizontalHeaderLabels(["Hash", "State","Score", "First seen", "Last seen"])
        self.verticalHeader().setVisible(False)

        for fila, (_, hash, state, score, fs, ls) in enumerate(data):
            self.setItem(fila, 0, QTableWidgetItem(str(hash)))
            self.setItem(fila, 1, QTableWidgetItem(str(state)))
            self.setItem(fila, 2, QTableWidgetItem(str(score)))
            self.setItem(fila, 3, QTableWidgetItem(str(fs)))
            self.setItem(fila, 4, QTableWidgetItem(str(ls)))

    def getData(self):
        conn = sqlite3.connect(self.databaseName)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hashes")  

        rows = cursor.fetchall()

        conn.close()
        return rows
    def getRowsNumber(self):
        data = self.getData()
        return len(data)