import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QSizePolicy, QTextEdit
)
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtCore import Qt, QTimer

import pyqtgraph as pg

class WaterQualityWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #f5f5f5; color: #1f2937;")

        self.cards = {}   # Dictionary to hold card label references
        self.pm_plot_widget = None  # For graph access

        self.init_ui()
        self.start_emulator()  # Start virtual sensor

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10) # Space between elements
        
        # Top summary cards (1st row)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        cards_layout.addWidget(self.create_card("pH Level", "--"))
        cards_layout.addWidget(self.create_card("Dissolve Oxygen", "--"))
        cards_layout.addWidget(self.create_card("Temperature", "--"))
        main_layout.addLayout(cards_layout)

        # Top summary cards (2nd row)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        cards_layout.addWidget(self.create_card("TDS", "--"))
        cards_layout.addWidget(self.create_card("Turbidity", "--"))
        cards_layout.addWidget(self.create_card("Conductivity", "--"))
        main_layout.addLayout(cards_layout)

        # Chart area
        chart_layout = QHBoxLayout()
        chart_layout.setSpacing(10)
        chart_layout.addWidget(self.create_graph("pH/DO"))
        main_layout.addLayout(chart_layout)

        self.setLayout(main_layout)

    def create_card(self, title, value):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #42a5f5;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel {
                color: black;
            }
        """)
        layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 14, QFont.Bold))
        value_lbl = QLabel(value)
        value_lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        card.setLayout(layout)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.cards[title] = value_lbl  # Store reference for later
        return card


    def create_graph(self, title):
        # Frame for rounded corner effect
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        label = QLabel(title)
        label.setFont(QFont("Arial", 12, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #1f2937;")
        layout.addWidget(label)

        # Plot widget with multi-line graph
        self.pm_plot_widget = pg.PlotWidget()
        self.pm_plot_widget.setBackground("#ffffff")
        self.pm_plot_widget.setLabel("left", "Level", **{"color": "#1f2937", "font-size": "12px"})
        self.pm_plot_widget.setLabel("bottom", "Time", **{"color": "#1f2937", "font-size": "12px"})
        self.pm_plot_widget.showGrid(x=True, y=True)

        layout.addWidget(self.pm_plot_widget)
        frame.setLayout(layout)
        return frame

    def start_emulator(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fake_sensor_data)
        self.timer.start(5 * 1000)  # update every 10 seconds

    def update_fake_sensor_data(self):
        ph = round(random.uniform(6.5, 8.5), 2)
        oxygen = round(random.uniform(6.0, 9.0), 2)
        temp = round(random.uniform(10.0, 30.0), 1)
        tds = round(random.uniform(300, 900), 1)
        turb = round(random.uniform(1.0, 100.0), 1)
        cond = round(random.uniform(400, 1000), 1)

        self.cards["pH Level"].setText(f"{ph}")
        self.cards["Dissolve Oxygen"].setText(f"{oxygen} mg/L")
        self.cards["Temperature"].setText(f"{temp} °C")
        self.cards["TDS"].setText(f"{tds} mg/L")
        self.cards["Turbidity"].setText(f"{turb} NTU")
        self.cards["Conductivity"].setText(f"{cond} µS/cm")

        # Update graph (basic trend)
        x = list(range(10))
        y1 = [random.uniform(6.5, 8.5) for _ in x]  # pH
        y2 = [random.uniform(6.0, 9.0) for _ in x]  # DO

        self.pm_plot_widget.clear()
        self.pm_plot_widget.plot(x, y1, pen=pg.mkPen("#2563eb", width=2))
        self.pm_plot_widget.plot(x, y2, pen=pg.mkPen("#10b981", width=2))