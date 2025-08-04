import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load environment variables
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")  # Facebook Page Access Token
IG_BUSINESS_ID = os.getenv("IG_USER_ID")       # Instagram Business Account ID (optional)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "123456789")  # Webhook verification token
DX_API_SEND_MESSAGE = os.getenv("DX_API_SEND_MESSAGE")

# Correct Facebook Graph API endpoint for sending messages
FB_GRAPH_URL = "https://graph.facebook.com/v19.0/me/messages"
sender_map = {}

@app.route("/")
def home():
    return "✅ Instagram bot is running."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verified")
            return challenge, 200
        else:
            print("❌ Webhook verification failed")
            return "Verification failed", 403

    elif request.method == "POST":
        data = request.get_json()
        print("📥 Incoming Data:")
        print(json.dumps(data, indent=4))

        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    sender_id = event["sender"]["id"]
                    
                    if event.get("message", {}).get("is_echo"):
                        print("🔁 Ignored echo message.")
                        continue

                    if "message" in event:
                        user_message = event["message"].get("text", "")
                        print(f"📩 Message from {sender_id}: {user_message}")
                        
                        chat_id = sender_id
                        sender_map[chat_id] = sender_id

                        send_via_dx_api(chat_id=chat_id, message_text=user_message)

        return "OK", 200

def send_text_message(recipient_id, message_text):
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}

    response = requests.post(FB_GRAPH_URL, params=params, headers=headers, json=payload)
    
    print("💬 IG Message Response:")
    print(response.status_code)
    print(response.text)

    if response.status_code != 200:
        print("❌ Failed to send message. Please check recipient ID and access token.")
        
def send_via_dx_api(chat_id, message_text):
    if not DX_API_SEND_MESSAGE:
        print("❌ DX_API_SEND_MESSAGE URL is not set.")
        return
    
    payload = {
        "chat_id": chat_id,
        "user_message": message_text,
        "file_ids": [],
        "file_urls": [],
        "callback_type": "instagram",
    }

    try:
        response = requests.post(DX_API_SEND_MESSAGE, json=payload)
        print("📤 DX API Response:")
        print(response.status_code)
        print(response.text)

        if response.status_code != 200:
            print("❌ Failed to send message via DX API.")
    except Exception as e:
        print(f"❌ Exception during DX API call: {e}")
        
@app.route("/dx-result", methods=["POST"])
def dxmind_result():
    data = request.get_json()
    chat_id = data.get("chat_id")
    ai_response = data.get("ai_response")
    sender_id = sender_map.get(chat_id)
    
    print(f"📥 DX Result Received: {data}")
    
    if ai_response and sender_id:
        send_text_message(sender_id, ai_response)
        return jsonify({"status": "message sent"}), 200
    else:
        print("❌ Missing sender_id or ai_response")
        return jsonify({"error": "Missing sender_id or ai_response"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
