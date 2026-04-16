import sys
from collections import deque
import psutil
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Memory_widget(QWidget):
    def __init__(self, interval_ms=100, max_points=100, limit_mb=500):
        super().__init__()

        self.interval_ms = interval_ms
        self.max_points = max_points
        self.limit_mb = limit_mb

        self.used_data = deque(maxlen=max_points)
        self.free_data = deque(maxlen=max_points)

        self.setWindowTitle("Monitor RAM en tiempo real")
        self.resize(900, 500)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_memory)
        self.timer.start(self.interval_ms)

        self.setStyleSheet("background-color:darkgray")

    import sys
from collections import deque
import psutil
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Memory_widget(QWidget):
    def __init__(self, interval_ms=100, max_points=100, limit_mb=500):
        super().__init__()

        self.interval_ms = interval_ms
        self.max_points = max_points
        self.limit_mb = limit_mb

        self.used_data = deque(maxlen=max_points)
        self.free_data = deque(maxlen=max_points)

        self.setWindowTitle("Monitor RAM en tiempo real")
        self.resize(900, 500)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_memory)
        self.timer.start(self.interval_ms)

        self.setStyleSheet("background-color:darkgray")

    def update_memory(self):
        mem = psutil.virtual_memory()
        used_mb = mem.used / 1024 / 1024
        free_mb = mem.available / 1024 / 1024

        self.used_data.append(used_mb)
        self.free_data.append(free_mb)

        self.ax.clear()
        self.ax.plot(self.used_data, label="RAM usada")
        self.ax.plot(self.free_data, label="RAM libre")
        self.ax.set_title("Memoria en tiempo real")
        self.ax.set_ylabel("MB")
        self.ax.grid(True)
        self.ax.legend()

        if free_mb < self.limit_mb:
            self.ax.set_title("Low memory", fontsize=14)

        self.canvas.draw()
