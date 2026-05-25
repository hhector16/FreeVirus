from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from datetime import datetime
from databases import hash_cache
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class InstancesTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(800)
        self.setFrameStyle(0)  
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # quitar scroll horizontal   
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)    # scroll vertical solo si hace falta
        self.databaseName = os.path.join(BASE_DIR,"..","databases", "instances.db")

        self.setHorizontalHeaderLabels(["Hash", "Date","Pid", "Ppid", "Path", "Event"])
        self.verticalHeader().setVisible(False)
        self.setColumnCount(6)


        if not os.path.exists(self.databaseName):
            hash_cache.init_instances_db()
        else:
            data = self.getData()

            self.setRowCount(len(data))

            

            for fila, (_, hash, fecha, pid, ppid, path, event) in enumerate(data):
                self.setItem(fila, 0, QTableWidgetItem(str(hash)))
                self.setItem(fila, 1, QTableWidgetItem(str(datetime.fromtimestamp(fecha))))
                self.setItem(fila, 2, QTableWidgetItem(str(pid)))
                self.setItem(fila, 3, QTableWidgetItem(str(ppid)))
                self.setItem(fila, 4, QTableWidgetItem(str(path)))
                self.setItem(fila, 5, QTableWidgetItem(str(event)))




    def getData(self):
        conn = sqlite3.connect(self.databaseName)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM instances")  

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

        for fila, (_, hash, fecha, pid, ppid, path, event) in enumerate(data):
                self.setItem(fila, 0, QTableWidgetItem(str(hash)))
                self.setItem(fila, 1, QTableWidgetItem(str(datetime.fromtimestamp(fecha))))
                self.setItem(fila, 2, QTableWidgetItem(str(pid)))
                self.setItem(fila, 3, QTableWidgetItem(str(ppid)))
                self.setItem(fila, 4, QTableWidgetItem(str(path)))
                self.setItem(fila, 5, QTableWidgetItem(str(event)))