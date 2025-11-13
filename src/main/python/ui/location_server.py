import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# JSON file path
LOCATION_FILE = "location.json"

# Default location data
def get_default_location():
    return {
        "selected": {
            "name": "Kolkata, India",
            "lat": 22.5726,
            "lon": 88.3639
        },
        "presets": {
            "Delhi": {"lat": 28.6139, "lon": 77.2090},
            "Mumbai": {"lat": 19.0760, "lon": 72.8777},
            "Chennai": {"lat": 13.0827, "lon": 80.2707},
            "Ranchi": {"lat": 23.3441, "lon": 85.3096},
            "Bangalore": {"lat": 12.9716, "lon": 77.5946},
            "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "Jaipur": {"lat": 26.9124, "lon": 75.7873},
            "Lucknow": {"lat": 26.8467, "lon": 80.9462}
        }
    }

# Initialize JSON file if not exists
if not os.path.exists(LOCATION_FILE):
    with open(LOCATION_FILE, "w") as f:
        json.dump(get_default_location(), f, indent=4)

@app.route("/location", methods=[POST])
def update_location():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        name = request.args.get("name", "Unknown Location")

        with open(LOCATION_FILE, "r") as f:
            data = json.load(f)

        data["selected"] = {
            "name": name,
            "lat": lat,
            "lon": lon
        }

        with open(LOCATION_FILE, "w") as f:
            json.dump(data, f, indent=4)

        print(f"[Location Saved] {name} - {lat}, {lon}")
        return jsonify({"status": "success", "lat": lat, "lon": lon})
    except Exception as e:
        print("[Error Saving Location]", str(e))
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/location/default")
def get_current_location():
    try:
        with open(LOCATION_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data.get("selected", {}))
    except:
        return jsonify(get_default_location()["selected"])

@app.route("/location/presets")
def get_presets():
    try:
        with open(LOCATION_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data.get("presets", {}))
    except:
        return jsonify(get_default_location()["presets"])

if __name__ == "__main__":
    app.run(port=5000)
