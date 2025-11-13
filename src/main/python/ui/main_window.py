import sys
import os
import json
import webbrowser
import requests

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QHBoxLayout, QStackedWidget, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

from ui.welcome_page import IntroWidget
from ui.modules.air_quality.air_gui import AirQualityWidget
from ui.modules.water_quality.water_gui import WaterQualityWidget
from ui.modules.weather_forecast.weather_gui import WeatherForecastWidget

LOCATION_FILE = "src/main/python/ui/location.json"
GEOLOCATION_HTML = "src/main/python/ui/geolocation.html"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Environmental Monitoring and Control System")
        self.resize(1400, 800)
        self.setWindowIcon(QIcon("src/main/python/ui/resources/icons/EMCS_icons.png"))

        self.sidebar_expanded = True
        self.current_theme = "light"
        self.current_language = "English"

        self.init_ui()
        self.try_auto_fetch_location()

    def try_auto_fetch_location(self):
        try:
            # If location already exists, do nothing
            if os.path.exists(LOCATION_FILE):
                with open(LOCATION_FILE, "r") as f:
                    current = json.load(f).get("current", {})
                    if current.get("lat") and current.get("lon"):
                        return  # Already set

            # Try IP-based location
            response = requests.get("https://ipinfo.io/json")
            if response.status_code == 200:
                data = response.json()
                lat, lon = data.get("loc", "22.5726,88.3639").split(",")
                city = data.get("city", "Kolkata")
                with open(LOCATION_FILE, "r") as f:
                    loc_data = json.load(f)
                loc_data["current"] = {
                    "city": city,
                    "lat": lat,
                    "lon": lon,
                    "source": "system-ip"
                }
                with open(LOCATION_FILE, "w") as f:
                    json.dump(loc_data, f, indent=4)
                print(f"[Auto IP Location] {city}: {lat}, {lon}")
                return
        except Exception as e:
            print("[Auto Location IP Error]", e)

        # Fallback to browser location
        try:
            html_path = os.path.abspath(GEOLOCATION_HTML)
            webbrowser.open(f"file:///{html_path}")
        except Exception as e:
            print("[Open Geolocation HTML Error]", e)

    def set_active_page(self, index, title):
        self.stack.setCurrentIndex(index)
        self.buttons[title].setChecked(True)

    def apply_hover_glow(self, button):
        def on_enter(event):
            glow = QGraphicsDropShadowEffect()
            glow.setColor(QColor(0, 255, 255))  # Cyan glow
            glow.setOffset(0, 0)
            glow.setBlurRadius(20)
            button.setGraphicsEffect(glow)

        def on_leave(event):
            button.setGraphicsEffect(None)

        button.installEventFilter(self)
        button.enterEvent = on_enter
        button.leaveEvent = on_leave

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        layout = QHBoxLayout()
        central_widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar menu
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(270)
        self.sidebar.setStyleSheet("background-color: #fafbfc;")

        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar_layout.setAlignment(Qt.AlignTop)

        # Toggle Button
        # App logo and name (top branding header)
        self.logo_label = QLabel("🧪 EMCS")
        self.logo_label.setStyleSheet("color: black; font-size: 16px; font-weight: bold; padding: 10px;")
        self.sidebar_layout.addWidget(self.logo_label)

        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.toggle_btn.setStyleSheet("color: black; background-color: transparent;")
        self.sidebar_layout.addWidget(self.toggle_btn)

        # Sidebar Pages
        self.pages = {
            "Home": IntroWidget(),  # welcome page
            "Air Quality": AirQualityWidget(),
            "Water Quality": WaterQualityWidget(),
            "Weather Forecast": WeatherForecastWidget()
        }

        self.stack = QStackedWidget()
        for page in self.pages.values():
            # page.setAlignment(Qt.AlignCenter)
            self.stack.addWidget(page)

        self.buttons = {}
        for i, title in enumerate(self.pages.keys()): 
            icon_paths = {
                "Home": "src/main/python/ui/resources/icons/home-icon.png",
                "Air Quality": "src/main/python/ui/resources/icons/air_quality.png",
                "Water Quality": "src/main/python/ui/resources/icons/water_quality.png",
                "Weather Forecast": "src/main/python/ui/resources/icons/weather_forecast.png"
            }
            btn = QPushButton(title)
            btn.setIcon(QIcon(icon_paths[title]))
            btn.setIconSize(QSize(48, 48))  # Adjust icon size as needed
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setToolTip(title)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            btn.clicked.connect(lambda checked, index=i, t=title: self.set_active_page(index, t))
            btn.setStyleSheet("""
                QPushButton {
                    color: black;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 12px;
                    text-align: left;
                    background-color: transparent;
                    border: none
                }
                QPushButton:hover {
                    background-color: #7cf7f7;
                    border-radius: 6px
                }
            """)
            self.sidebar_layout.addWidget(btn)
            self.buttons[title] = btn
            self.apply_hover_glow(btn)

        self.sidebar_layout.addStretch()

        # Exit Button
        exit_btn = QPushButton("  Exit")
        exit_btn.setIcon(QIcon("src/main/python/ui/resources/icons/exit_button.png"))
        exit_btn.setIconSize(QSize(42, 42))
        exit_btn.setToolTip("Close the application")
        exit_btn.setStyleSheet("""
            QPushButton {
                color: red;
                font-weight: bold;
                font-size: 16px;
                padding: 12px;
                text-align: left;
                background-color: transparent;
                border: none
            }
            QPushButton:hover {
                background-color: #ffc4c4;
                border-radius: 6px
            }
        """)
        exit_btn.clicked.connect(self.close_app)
        self.sidebar_layout.addWidget(exit_btn, alignment=Qt.AlignBottom)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        # --- Footer section in sidebar ---
        footer_layout = QVBoxLayout()
        footer_layout.setAlignment(Qt.AlignBottom)

        # Language Selector
        #self.language_combo = QComboBox()
        #self.language_combo.addItems(["English", "Hindi", "Bengali"])
        #self.language_combo.currentTextChanged.connect(self.change_language)
        #footer_layout.addWidget(self.language_combo)
        #self.sidebar_layout.addLayout(footer_layout)

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.setFixedWidth(95)
            self.logo_label.setText("🧪")
            self.toggle_btn.setText("▶")
            for btn in self.buttons.values():
                btn.setText("")  # Hide labels
            self.sidebar_expanded = False
        else:
            self.sidebar.setFixedWidth(270)
            self.logo_label.setText("🧪 EMCS")
            self.toggle_btn.setText("☰")
            for name, btn in self.buttons.items():
                btn.setText(name)
            self.sidebar_expanded = True

    #def change_language(self, language):
        #self.current_language = language
        #(Optional) Update UI translation logic here

    def close_app(self):
        print("[Exit] Closing app and cleaning up...")
        self.close()
        sys.exit(0)