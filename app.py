from flask import Flask, request, jsonify, send_file
import os
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)

BASE_PRICE = 100
PRICE_PER_KM = 25
DELIVERY_EXTRA = 50

rides = []

# Distance calculator (Haversine formula)
def calculate_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

@app.route("/")
def home():
    return "🚖 Taxi Aleeher API LIVE"

@app.route("/ride", methods=["POST"])
def create_ride():
    data = request.json
    
    lat1 = float(data["pickup_lat"])
    lon1 = float(data["pickup_lon"])
    lat2 = float(data["drop_lat"])
    lon2 = float(data["drop_lon"])
    service = data["service"]

    distance = calculate_distance(lat1, lon1, lat2, lon2)
    total = BASE_PRICE + (distance * PRICE_PER_KM)

    if service == "delivery":
        total += DELIVERY_EXTRA

    ride = {
        "date": datetime.now(),
        "distance_km": round(distance, 2),
        "service": service,
        "total": round(total, 2)
    }

    rides.append(ride)

    return jsonify(ride)

@app.route("/admin")
def admin():
    return jsonify(rides)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
