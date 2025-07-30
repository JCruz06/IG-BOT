from fastapi import FastAPI, Request, Query, HTTPException, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging
import requests

# Load environment variables
load_dotenv()
IG_API_KEY = os.getenv("IG_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

@app.get("/")
async def home():
    return {
        "status": "Running server" 
    }

# Webhook verification route (GET)
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None),
    hub_verify_token: str = Query(None),
    hub_challenge: str = Query(None)
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Invalid verification token")


# Webhook message receiving (POST)
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    logger.info(f"📥 Webhook received: {data}")

    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]
            message_text = messaging.get("message", {}).get("text", "").lower().strip()

            logger.info(f"📨 Message from {sender_id}: {message_text}")

            if message_text == "hi":
                reply = "Hello! Welcome sa aking business account. Thanks for saying hi. How can I help you?"
            else:
                reply = "Hindi man lang nag Hi!"

            send_message(sender_id, reply)

    return {"status": "ok"}


def send_message(recipient_id: str, text: str):
    url = "https://graph.facebook.com/v19.0/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE"
    }
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "IG_API_KEY": IG_API_KEY
    }
    response = requests.post(url, params=params, json=payload, headers=headers)
    logger.info(f"✅ Sent message to {recipient_id}: {text}, Status: {response.status_code}")
