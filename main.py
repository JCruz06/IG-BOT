import os
import json
import requests
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

app = FastAPI()

# Load environment variables
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
IG_BUSINESS_ID = os.getenv("IG_USER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "123456789")
DX_API_SEND_MESSAGE = os.getenv("DX_API_SEND_MESSAGE")

FB_GRAPH_URL = "https://graph.facebook.com/v19.0/me/messages"
sender_map = {}

@app.get("/", response_class=PlainTextResponse)
async def home():
    return "✅ Instagram bot is running."

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        print("✅ Webhook verified")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    print("❌ Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
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

    return PlainTextResponse(content="OK", status_code=200)

def send_text_message(recipient_id: str, message_text: str):
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

def send_via_dx_api(chat_id: str, message_text: str):
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

@app.post("/dx-result")
async def dxmind_result(request: Request):
    data = await request.json()
    chat_id = data.get("chat_id")
    ai_response = data.get("ai_response")
    sender_id = sender_map.get(chat_id)

    print(f"📥 DX Result Received: {data}")

    if ai_response and sender_id:
        send_text_message(sender_id, ai_response)
        return JSONResponse(content={"status": "message sent"}, status_code=200)
    else:
        print("❌ Missing sender_id or ai_response")
        return JSONResponse(content={"error": "Missing sender_id or ai_response"}, status_code=400)

# Optional: To run the server if you save this script as `main.py`
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
