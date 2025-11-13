import os
import json
import geocoder
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy, QCompleter
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

class AirQualityWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.lat = None
        self.lon = None

        self.setStyleSheet("background-color: #f9fafb; color: #111827;")
        
        self.api_key = "your api key"  # Replace with your actual OpenWeather API key

        self.init_ui()

        self.load_location()  # Load initial IP-based location or fallback
        self.setup_autocomplete()
        self.fetch_air_quality_data()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # 🔍 1. Search Bar (Circular)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("🔍 Search Location (India only)")
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

        # 🧭 2. Location Summary Section
        self.summary_bar = QFrame()
        self.summary_bar.setMaximumHeight(80)
        self.summary_bar.setStyleSheet("""
            QFrame {
                background-color: #e0f2ff;
                border: 2px solid #90caf9;
                border-radius: 20px;
                padding: 5px;
            }
        """)
        summary_layout = QHBoxLayout(self.summary_bar)
        self.label_location = QLabel("Location: -- (Timezone: --)")
        self.label_location.setFont(QFont("Arial", 10))

        self.label_temp = QLabel("Min: --°C / Max: --°C")
        self.label_temp.setFont(QFont("Arial", 10))
        self.label_temp.setAlignment(Qt.AlignRight)

        summary_layout.addWidget(self.label_location, alignment=Qt.AlignLeft)
        summary_layout.addWidget(self.label_temp, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.summary_bar)

        # 🌫️ 3. Pollutant Cards Section
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(10)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.card_widgets = {}

        # Two rows
        pollutants = [
            "co", "no", "no2", "o3", "so2",   # Row 1
            "nh3", "aqi", "pm2_5", "pm10"     # Row 2
        ]

        for i, key in enumerate(pollutants):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #42a5f5;
                }
                QFrame:hover {
                    background-color: #f9fafb;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            label_title = QLabel(key.upper())
            label_title.setFont(QFont("Arial", 12, QFont.Bold))
            label_value = QLabel("--")
            label_value.setFont(QFont("Arial", 10, QFont.Bold))
            label_value.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(label_title)
            card_layout.addWidget(label_value)

            self.card_widgets[key] = label_value
            row = 0 if i < 5 else 1
            col = i if i < 5 else i - 5
            self.cards_grid.addWidget(card, row, col)

        self.main_layout.addLayout(self.cards_grid)

        # 🗺️ 4. Map Section
        self.map = QWebEngineView()
        self.map.setMinimumHeight(300)
        self.map.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.map)

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
        # 🔄 Load location from device (fallback handled)
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

                self.fetch_air_quality_data()

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

    def fetch_air_quality_data(self):
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
        try:
            res = requests.get(url)
            data = res.json()
            DEBUG = False
            if DEBUG:
                print("[API Response]", data)

            if "list" in data and data["list"]:
                components = data["list"][0]["components"]
                aqi = data["list"][0]["main"]["aqi"]
                # Set values
                for key in self.card_widgets:
                    if key == "aqi":
                        self.card_widgets[key].setText(str(aqi))
                    else:
                        val = components.get(key, "--")
                        self.card_widgets[key].setText(f"{val:.2f}" if isinstance(val, float) else str(val))

            # Load map layer after data is fetched
            self.fetch_weather_info()  # fetch current location info
            self.load_map()

        except Exception as e:
            DEBUG = False
            if DEBUG:
                print("[API Fetch Error]:", e)

    def fetch_weather_info(self):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric"
        try:
            res = requests.get(url)
            data = res.json()
            DEBUG = False
            if DEBUG:
                print("[Weather API]", data)

            city = data.get("name", "--")
            tz_offset = data.get("timezone", 0) // 3600
            temp_min = data["main"].get("temp_min", "--")
            temp_max = data["main"].get("temp_max", "--")

            self.label_location.setText(f"📍 {city} (Timezone: GMT+{tz_offset})")
            self.label_temp.setText(f"Min: {temp_min}°C / Max: {temp_max}°C")

        except Exception as e:
            DEBUG = False
            if DEBUG:
                print("[Weather Info Error]:", e)

    def load_map(self):

        lat, lon = self.lat, self.lon
        zoom = 5

        # Available layers with display names
        layers = {
            "Convective Precipitation (PAC0) [mm]": "PAC0",
            "Precipitation Intensity (PR0) [mm/s]": "PR0",
            "Accumulated Precipitation (PA0) [mm]": "PA0",
            "Accum. Precipitation - Rain (PAR0) [mm]": "PAR0",
            "Accum. Precipitation - Snow (PAS0) [mm]": "PAS0",
            "Snow Depth (SD0) [m]": "SD0",
            "Wind Speed 10m (WS10) [m/s]": "WS10",
            "Wind Speed + Dir (WND) [m/s]": "WND",
            "Atmospheric Pressure (APM) [hPa]": "APM",
            "Air Temp 2m (TA2) [°C]": "TA2",
            "Dew Point Temp (TD2) [°C]": "TD2",
            "Soil Temp 0-10cm (TS0) [K]": "TS0",
            "Soil Temp >10cm (TS10) [K]": "TS10",
            "Relative Humidity (HRD0) [%]": "HRD0",
            "Cloudiness (CL) [%]": "CL"
        }

        html_layers = ""
        for name, op in layers.items():
            tile_url = f"https://maps.openweathermap.org/maps/2.0/weather/{op}/{{z}}/{{x}}/{{y}}?appid={self.api_key}&fill_bound=true&opacity=0.6"
            html_layers += f"""
            var {op} = L.tileLayer('{tile_url}', {{
                maxZoom: 10,
                attribution: 'Weather Map © <a href="https://openweathermap.org/">OpenWeatherMap</a>'
            }});\n
            """

        layer_dict_entries = ",\n".join([f'"{name}": {op}' for name, op in layers.items()])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                html, body {{
                    height: 100%;
                    margin: 0;
                }}
                #mapid {{
                    height: 100%;
                    width: 100%;
                }}
            </style>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        </head>
        <body>
            <div id="mapid"></div>
            <script>
                var map = L.map('mapid').setView([{lat}, {lon}], {zoom});

                {html_layers}

                var baseMaps = {{}};
                var overlayMaps = {{
                    {layer_dict_entries}
                }};

                var defaultLayer = Object.values(overlayMaps)[0];
                defaultLayer.addTo(map);

                L.control.layers(baseMaps, overlayMaps, {{collapsed: true}}).addTo(map);

                L.marker([{lat}, {lon}]).addTo(map)
                    .bindPopup("You are here")
                    .openPopup();
            </script>
        </body>
        </html>
        """

        self.map.setHtml(html)
