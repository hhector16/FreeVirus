from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime
from databases import hash_cache

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class HashTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(800)
        self.setFrameStyle(0)  
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # delete x scroll
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)    # y scroll if needed
        self.databaseName = os.path.join(BASE_DIR,"..","databases", "hashes.db")

        self.setHorizontalHeaderLabels(["Hash", "State","Score", "First seen", "Last seen"])
        self.verticalHeader().setVisible(False)
        self.setColumnCount(5)


        if not os.path.exists(self.databaseName):
            hash_cache.init_hashes_db()
        else:

            data = self.getData()

            self.setRowCount(len(data))

            

            for fila, (_, hash, state, score, fs, ls) in enumerate(data):
                self.setItem(fila, 0, QTableWidgetItem(str(hash)))
                self.setItem(fila, 1, QTableWidgetItem(str(state)))
                self.setItem(fila, 2, QTableWidgetItem(str(score)))
                self.setItem(fila, 3, QTableWidgetItem(str(datetime.fromtimestamp(fs))))
                self.setItem(fila, 4, QTableWidgetItem(str(datetime.fromtimestamp(ls))))

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

    def refresh(self):
        data = self.getData()

        self.setRowCount(0)
        self.setRowCount(len(data))

        for fila, (_, hash, state, score, fs, ls) in enumerate(data):
            self.setItem(fila, 0, QTableWidgetItem(str(hash)))
            self.setItem(fila, 1, QTableWidgetItem(str(state)))
            self.setItem(fila, 2, QTableWidgetItem(str(score)))
            self.setItem(fila, 3, QTableWidgetItem(str(datetime.fromtimestamp(fs))))
            self.setItem(fila, 4, QTableWidgetItem(str(datetime.fromtimestamp(ls))))