import os
import json
import requests
from flask import Flask, request, redirect

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("APP_SETTINGS_GEN")
PAGE_ID = os.getenv("IG_USER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "123456789")
API_URL = f"https://graph.facebook.com/v19.0/{PAGE_ID}/messages"

@app.route("/")
def test():
    return "<p>Instagram Messaging Bot is running.</p>"

@app.route("/privacy_policy")
def privacy_policy():
    try:
        with open("privacy_policy.html", "rb") as file:
            privacy_policy_html = file.read()
        return privacy_policy_html
    except FileNotFoundError:
        return "<p>Privacy policy not found.</p>", 404

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Webhook verification
        hub_mode = request.args.get("hub.mode")
        hub_challenge = request.args.get("hub.challenge")
        hub_verify_token = request.args.get("hub.verify_token")
        if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
            return hub_challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == "POST":
        data = request.get_json()
        print(json.dumps(data, indent=4))  # Log incoming message

        if data.get("entry"):
            for entry in data["entry"]:
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event["sender"]["id"]

                    if "message" in messaging_event:
                        message = messaging_event["message"]

                        # Check for quick reply payload
                        if "quick_reply" in message:
                            payload = message["quick_reply"]["payload"]
                            handle_quick_reply(sender_id, payload)
                        else:
                            send_quick_replies(sender_id)

        return "OK", 200

def send_quick_replies(recipient_id):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "text": "How can I help you today?",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Track Order",
                    "payload": "TRACK_ORDER"
                },
                {
                    "content_type": "text",
                    "title": "Store Hours",
                    "payload": "STORE_HOURS"
                },
                {
                    "content_type": "text",
                    "title": "Contact Support",
                    "payload": "CONTACT_SUPPORT"
                }
            ]
        }
    }
    send_message(payload)

def handle_quick_reply(recipient_id, payload):
    if payload == "TRACK_ORDER":
        text = "Sure! Please provide your order number."
    elif payload == "STORE_HOURS":
        text = "We're open from 9 AM to 6 PM, Monday to Saturday."
    elif payload == "CONTACT_SUPPORT":
        text = "You can reach our support at support@example.com."
    else:
        text = "Sorry, I didn't understand that option."

    send_text_message(recipient_id, text)

def send_text_message(recipient_id, message_text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    send_message(payload)

def send_message(payload):
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    response = requests.post(API_URL, params=params, headers=headers, json=payload)
    print(f"Sent message: {response.status_code} - {response.text}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)