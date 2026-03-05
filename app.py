from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)

# ====== WHATSAPP CONFIG ======
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ====== TAXI PRICING ======
BASE_PRICE = 100
PRICE_PER_KM = 25
DELIVERY_EXTRA = 50

rides = []

# ====== DISTANCE CALCULATOR ======
def calculate_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

# ====== HOME ======
@app.route("/")
def home():
    return "🚖 Taxi Aleeher API + WhatsApp Bot LIVE"

# ====== WHATSAPP WEBHOOK VERIFY ======
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# ====== WHATSAPP RECEIVE MESSAGE ======
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data.get("entry"):
        changes = data["entry"][0]["changes"][0]["value"]
        messages = changes.get("messages")

        if messages:
            from_number = messages[0]["from"]

            send_whatsapp_message(
                from_number,
                "🚕 Byenvini nan Taxi ALEEHER!\nEkri 1 pou mande yon taxi."
            )

    return "OK", 200

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }

    requests.post(url, headers=headers, json=payload)

# ====== CREATE RIDE ======
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
        "date": datetime.now().isoformat(),
        "distance_km": round(distance, 2),
        "service": service,
        "total": round(total, 2)
    }

    rides.append(ride)

    return jsonify(ride)

# ====== ADMIN ======
@app.route("/admin")
def admin():
    return jsonify(rides)

# ====== RUN ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)