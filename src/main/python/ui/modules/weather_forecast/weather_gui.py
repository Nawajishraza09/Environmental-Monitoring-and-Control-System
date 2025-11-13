import os
import json
import geocoder
import requests
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCompleter,
    QLabel, QFrame, QSizePolicy, QScrollArea, QSpacerItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

class WeatherForecastWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #f5f5f5; color: #1f2937;")

        self.all_data = {}
        self.selected_day = None

        self.icon_map = {
            "Clear": "☀️",
            "Rain": "🌧️",
            "Clouds": "☁️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Partly Cloudy": "🌤️",
            "Heavy Rain": "🌧️💧",
            "Fog": "🌫️",
            "Mist": "🌫️",
            "Smoke": "🌫️",
            "Haze": "🌫️",
            "Overcast": "☁️☁️",
            "Moonlight": "🌙",
            "--": "❓"
        }

        self.api_key = "your api key"  # Replace with your actual OpenWeather API key
        
        self.init_ui()

        self.load_location()   # Load initial IP-based location or fallback
        self.setup_autocomplete()  
        self.fetch_all_weather_data()

        # Auto refresh every 10 minutes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_all_weather_data)
        self.timer.start(10 * 60 * 1000)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Search box
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("🔍 Search Location (India Only)")
        self.location_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        self.location_input.returnPressed.connect(self.handle_location_search)
        self.main_layout.addWidget(self.location_input)

        # Location summary circular bar
        self.summary_bar = QFrame()
        self.summary_bar.setMaximumHeight(80)
        self.summary_bar.setStyleSheet("""
            QFrame {
                background-color: #e0f2ff;
                border: 2px solid #90caf9;
                border-radius: 20px;
                padding: 2px;
            }
        """)
        summary_layout = QHBoxLayout(self.summary_bar)
        self.label_location = QLabel("Location: -- (Timezone: --)")
        self.label_location.setFont(QFont("Arial", 12))
        self.label_suntrack = QLabel("☀️ sunrise ---☀️--- sunset")
        self.label_suntrack.setFont(QFont("Arial", 12))
        self.label_temp_sun = QLabel("Min: --°C / Max: --°C | 🌅 -- | 🌇 --")
        self.label_temp_sun.setFont(QFont("Arial", 12))
        summary_layout.addWidget(self.label_location, alignment=Qt.AlignLeft)
        summary_layout.addWidget(self.label_suntrack, alignment=Qt.AlignCenter)
        summary_layout.addWidget(self.label_temp_sun, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.summary_bar)

        # --- Daily Forecast Fixed Row ---
        self.daily_container = QWidget()
        self.daily_container.setFixedHeight(200)
        self.daily_layout = QHBoxLayout(self.daily_container)
        self.daily_layout.setSpacing(10)
        self.daily_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.daily_container)

        # --- Hourly Forecast Cards ---
        self.hourly_container = QWidget()
        self.hourly_layout = QVBoxLayout(self.hourly_container)
        self.hourly_layout.setSpacing(10)
        self.hourly_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.hourly_container)

    def setup_autocomplete(self):
        try:
            path = os.path.abspath("src/main/python/ui/location.json")
            with open(path, "r") as f:
                data = json.load(f)
            suggestions = list(data.get("cities", {}).keys())
            completer = QCompleter(suggestions)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.location_input.setCompleter(completer)
        except Exception as e:
            DEBUG = False
            if DEBUG:
                print("[Autocomplete Setup Error]:", e)

    def load_location(self):
        try:
            g = geocoder.ip('me')
            if g.ok and g.latlng:
                self.lat, self.lon = map(str, g.latlng)
                DEBUG = False
                if DEBUG:
                    print(f"[Auto Location] IP-based location detected: {self.lat}, {self.lon}")
            else:
                DEBUG = False
                if DEBUG:
                    raise ValueError("IP Geolocation failed, falling back to Kolkata.")
        except:
            DEBUG = False
            if DEBUG:
                print("[Fallback] IP Geolocation error:", e)
            return 22.57, 88.36
            DEBUG = False
            if DEBUG:
                print("[Fallback] Using Kolkata as default location.")

    def handle_location_search(self):
        query = self.location_input.text().strip().lower()
        try:
            path = os.path.abspath("src/main/python/ui/location.json")
            with open(path, "r") as f:
                data = json.load(f)

            # Make cities lookup case-insensitive
            normalized_cities = {k.lower(): v for k, v in data.get("cities", {}).items()}
            
            if query in normalized_cities:
                city = normalized_cities[query]
                self.lat, self.lon = city["lat"], city["lon"]
                DEBUG = False
                if DEBUG:
                    print(f"[Air Quality Search] Location found & loaded successfull: {query} -> ({self.lat}, {self.lon})")
                
                self.location_input.setStyleSheet("""  # Reset style if previously red
                    QLineEdit {
                        border: 2px solid #d1d5db;
                        border-radius: 20px;
                        padding: 8px 16px;
                        font-size: 14px;
                        background-color: white;
                    }
                """)

                self.fetch_all_weather_data()

            else:
                DEBUG = False
                if DEBUG:
                    print(f"[Air Quality Search] City '{query}' could not found.")
                self.location_input.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid red;
                        border-radius: 20px;
                        padding: 8px 16px;
                        font-size: 14px;
                        background-color: white;
                    }
                """)
        except Exception as e:
            DEBUG = False
            if DEBUG:
                print("[Air Quality Search] Failed to load location:", e)

    def fetch_all_weather_data(self):
        if not self.lat or not self.lon:
            return
        try:
            current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric"
            hourly_url = f"https://pro.openweathermap.org/data/2.5/forecast/hourly?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric"
            daily_url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={self.lat}&lon={self.lon}&cnt=7&appid={self.api_key}&units=metric"

            current = requests.get(current_url).json()
            hourly = requests.get(hourly_url).json()
            daily = requests.get(daily_url).json()

            self.process_data(current, hourly, daily)
        except Exception as e:
            DEBUG = False
            if DEBUG:
                print("[API Fetch Error]:", e)

    def process_data(self, current, hourly, daily):
        # Summary Bar Info
        location = current.get("name", "--")
        tz_offset = current.get("timezone", 0)
        timezone = f"GMT{'+' if tz_offset >= 0 else '-'}{abs(tz_offset) // 3600}"
        temp_min = round(current["main"].get("temp_min", 0))
        temp_max = round(current["main"].get("temp_max", 0))
        sunrise = datetime.utcfromtimestamp(current["sys"]["sunrise"] + tz_offset).strftime("%H:%M")
        sunset = datetime.utcfromtimestamp(current["sys"]["sunset"] + tz_offset).strftime("%H:%M")

        self.label_location.setText(f"📍 {location} (Timezone: {timezone})")
        self.label_temp_sun.setText(f"Min: {temp_min}°C / Max: {temp_max}°C | 🌅 {sunrise} | 🌇 {sunset}")
        self.label_suntrack.setText("☀️ " + sunrise + " ------☀️------ " + sunset)

        # Build daily card
        self.all_data = {}
        today = datetime.now()
        for i, entry in enumerate(daily["list"]):
            date_obj = datetime.utcfromtimestamp(entry["dt"]) + timedelta(seconds=tz_offset)
            date_key = date_obj.strftime("%b %d")
            weekday = date_obj.strftime("%A")

            self.all_data[date_key] = {
                "weekday": weekday,
                "temp": round(entry["temp"]["day"]),
                "summary": entry["weather"][0]["main"],
                "hourly": []
            }

        for h in hourly["list"]:
            dt = datetime.utcfromtimestamp(h["dt"]) + timedelta(seconds=tz_offset)
            date_key = dt.strftime("%b %d")
            time_24h = dt.strftime("%H:%M")

            if date_key in self.all_data:
                self.all_data[date_key]["hourly"].append({
                    "time": time_24h,
                    "temp": round(h["main"]["temp"]),
                    "status": h["weather"][0]["main"],
                    "humidity": h["main"]["humidity"],
                    "pressure": h["main"]["pressure"],
                    "wind_speed": h["wind"]["speed"],
                    "wind_deg": h["wind"]["deg"],
                    "gust": h["wind"].get("gust", 0)
                })

        self.render_daily_cards()
        self.render_hourly_cards(self.get_today_key())

    def render_daily_cards(self):
        for i in reversed(range(self.daily_layout.count())):
            widget = self.daily_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        sorted_days = list(self.all_data.keys())
        today_key = self.get_today_key()

        for i, day in enumerate(sorted_days):
            btn = QPushButton()
            btn.setFixedSize(150, 200)
            is_today = (day == today_key)
            enabled = i < 4  # Only 4 days allow hourly forecast

            style = """
                QPushButton {
                    background-color: #fff;
                    border-radius: 10px;
                    border: 2px solid #42a5f5;
                }
                QPushButton:hover {
                    background-color: #f9fafb;
                }
            """ if enabled else """
                QPushButton {
                    background-color: #f9fafb;
                    border-radius: 10px;
                    border: 2px solid #aaa;
                    color: #999;
                }
            """

            btn.setStyleSheet(style)
            btn.setEnabled(enabled)

            layout = QVBoxLayout(btn)
            layout.setContentsMargins(5, 5, 5, 5)

            lbl_day = QLabel(self.all_data[day]["weekday"])
            lbl_day.setAlignment(Qt.AlignCenter)
            lbl_day.setFont(QFont("Arial", 12, QFont.Bold))

            lbl_date = QLabel(day)
            lbl_date.setFont(QFont("Arial", 12, QFont.Bold))
            lbl_date.setAlignment(Qt.AlignCenter)

            icon = self.icon_map.get(self.all_data[day]["summary"], "❓")
            lbl_status = QLabel(f"{icon}\n{self.all_data[day]['summary']}")
            lbl_status.setFont(QFont("Arial", 10, QFont.Bold))
            lbl_status.setAlignment(Qt.AlignCenter)

            lbl_temp = QLabel(f"{self.all_data[day]['temp']}°C")
            lbl_temp.setFont(QFont("Arial", 10, QFont.Bold))
            lbl_temp.setAlignment(Qt.AlignCenter)

            layout.addWidget(lbl_day)
            layout.addWidget(lbl_date)
            layout.addWidget(lbl_status)
            layout.addWidget(lbl_temp)

            if enabled:
                btn.clicked.connect(lambda checked, d=day: self.render_hourly_cards(d))

            self.daily_layout.addWidget(btn)

    def render_hourly_cards(self, day):
        for i in reversed(range(self.hourly_layout.count())):
            widget = self.hourly_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        now = datetime.now().strftime("%H:%M")
        hourly_data = self.all_data[day]["hourly"]
        start_idx = next((i for i, h in enumerate(hourly_data) if h["time"] >= now), 0)
        display_data = hourly_data[start_idx:start_idx + 6]

        for hour in display_data:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 10px;
                }
            """)
            layout = QHBoxLayout(card)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(20)

            emoji = self.icon_map.get(hour["status"], "❓")

            time_label = QLabel(f"🕒 {hour['time']}")
            time_label.setFont(QFont("Arial", 10))
            layout.addWidget(time_label)
    
            temp_label = QLabel(f"🌡️ {hour['temp']} °C")
            temp_label.setFont(QFont("Arial", 10))
            layout.addWidget(temp_label)

            humid_label = QLabel(f"💧 {hour['humidity']}%")
            humid_label.setFont(QFont("Arial", 10))
            layout.addWidget(humid_label)

            pressure_label = QLabel(f"{hour['pressure']} hPa")
            pressure_label.setFont(QFont("Arial", 10))
            layout.addWidget(pressure_label)

            wind_label = QLabel(f"{hour['wind_speed']} km/h")
            wind_label.setFont(QFont("Arial", 10))
            layout.addWidget(wind_label)

            degree_label = QLabel(f"{hour['wind_deg']}° angle")
            degree_label.setFont(QFont("Arial", 10))
            layout.addWidget(degree_label)

            gust_label = QLabel(f"{hour['gust']} km/h")
            gust_label.setFont(QFont("Arial", 10))
            layout.addWidget(gust_label)

            status_label = QLabel(f"{emoji} {hour['status']}")
            status_label.setFont(QFont("Arial", 10))
            layout.addWidget(status_label)

            self.hourly_layout.addWidget(card)

    def get_today_key(self):
        return datetime.now().strftime("%b %d")
    
