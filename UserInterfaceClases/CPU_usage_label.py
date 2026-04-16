from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
import psutil


class CPU_usage_label(QWidget):
    def __init__(self, interval=1000, parent=None):
        super().__init__(parent)

        self.interval = interval
        self.labels = []

        self.layout = QHBoxLayout(self)

        self.setStyleSheet("margin-left:100px;border 1 solid black")

        container1=QWidget()
        container2=QWidget()
        container3=QWidget()

        layout1 = QVBoxLayout(container1)
        layout2 = QVBoxLayout(container2)
        layout3 = QVBoxLayout(container3)


        # labels principales
        for i in range(12):
            lbl = QLabel("...")
            lbl.setStyleSheet(
                "font-family: monospace;"
                "font-size: 12px;"
                "padding: 2px;"
                "color: darkgray"
            )
            if(i<4):
                layout1.addWidget(lbl)
            elif (i<8):
                layout2.addWidget(lbl)
            else:
                layout3.addWidget(lbl)
            self.labels.append(lbl)

        self.layout.addWidget(container1)
        self.layout.addWidget(container2)
        self.layout.addWidget(container3)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(self.interval)

        self.update_stats()

    def update_stats(self):
        cpu_total = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)

        freq = psutil.cpu_freq()
        stats = psutil.cpu_stats()

        physical = psutil.cpu_count(logical=False)
        logical = psutil.cpu_count(logical=True)

        try:
            load1, load5, load15 = psutil.getloadavg()
            load_text = f"{load1:.2f}, {load5:.2f}, {load15:.2f}"
        except:
            load_text = "N/A"

        values = [
            f"Total CPU: {cpu_total:.1f}%",
            f"Physical cores: {physical}",
            f"Logical threads: {logical}",
            f"Load: {load_text}",
            f"Frequency: {freq.current:.0f} MHz" if freq else "Frequency: N/A",
            f"Context switches: {stats.ctx_switches}",
            f"Interrupts: {stats.interrupts}",
            f"Soft interrupts: {stats.soft_interrupts}",
            f"System calls: {stats.syscalls}",
        ]

        # uso por núcleo
        for i, core in enumerate(per_core[:3]):  # primeros 3 cores
            values.append(f"Core {i}: {core:.1f}%")

        for i, text in enumerate(values):
            if i < len(self.labels):
                self.labels[i].setText(text)