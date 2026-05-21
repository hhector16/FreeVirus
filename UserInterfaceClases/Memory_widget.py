import sys
from collections import deque
import psutil
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Memory_widget(QWidget):
    def __init__(self, interval_ms=500, max_points=100, limit_mb=500):
        super().__init__()

        self.max_points = max_points
        self.limit_mb = limit_mb

        self.used_data = deque(maxlen=max_points)
        self.free_data = deque(maxlen=max_points)

        self.setStyleSheet("background-color:darkgray")

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.line_used, = self.ax.plot([], [], label="RAM usada")
        self.line_free, = self.ax.plot([], [], label="RAM libre")

        self.ax.set_title("Memoria en tiempo real")
        self.ax.set_ylabel("MB")
        self.ax.grid(True)
        self.ax.legend()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_memory)
        self.timer.start(interval_ms)

    def update_memory(self):
        mem = psutil.virtual_memory()

        used_mb = mem.used / 1024 / 1024
        free_mb = mem.available / 1024 / 1024

        self.used_data.append(used_mb)
        self.free_data.append(free_mb)

        self.line_used.set_data(range(len(self.used_data)), self.used_data)
        self.line_free.set_data(range(len(self.free_data)), self.free_data)

        self.ax.relim()
        self.ax.autoscale_view()

        if free_mb < self.limit_mb:
            self.ax.set_title("Low memory")
        else:
            self.ax.set_title("Memoria en tiempo real")

        self.canvas.draw_idle()