import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("GRAPH_API_ACCESS_TOKEN")          # PAGE Access Token
IG_USER_ID = os.getenv("IG_USER_ID")              # Instagram Business Account ID
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "123456")  # Webhook Verify Token

API_URL = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/messages"

@app.route("/")
def home():
    return "Instagram bot is running."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    elif request.method == "POST":
        data = request.get_json()
        print(json.dumps(data, indent=4))

        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event["sender"]["id"]

                    if "message" in messaging_event:
                        send_text_message(sender_id, "Hello from your bot!")

        return "OK", 200

def send_text_message(recipient_id, text):
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}

    response = requests.post(API_URL, params=params, headers=headers, json=payload)
    print(f"Sent message: {response.status_code} - {response.text}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)