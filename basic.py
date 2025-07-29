from instagrapi import Client
from dotenv import load_dotenv
import os
import logging
import time

# Load credentials
load_dotenv()
ACCOUNT_USERNAME = os.getenv("ACCOUNT_USERNAME")
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Instagram setup
cl = Client()
replied_threads = set()

def login():
    try:
        logged_in = cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
        if logged_in:
            logger.info("Logged into Instagram.")
            return True
        else:
            logger.error("Login failed.")
            return False
    except Exception as e:
        logger.exception(f"Exception during login: {e}")
        return False

def auto_reply_loop():
    logger.info("💬 Auto-reply loop started...")

    while True:
        try:
            threads = cl.direct_threads(selected_filter="unread", amount=20)
            logger.info(f"📥 Found {len(threads)} unread threads.")

            for thread in threads:
                thread_id = thread.id
                users = [u.username for u in thread.users]
                logger.info(f"Thread ID: {thread_id}, Users: {users}")

                messages = cl.direct_messages(thread_id, amount=1)
                if not messages:
                    continue

                message = messages[0]
                sender_id = message.user_id
                message_text = (message.text or "").strip().lower()

                if sender_id == cl.user_id:
                    continue

                logger.info(f"📨 Message from {sender_id}: {message.text}")

                if message_text == "hi":
                    reply_text = "Hello! Welcome sa aking business account. Thanks for saying hi. How can I help you?"
                else:
                    reply_text = "Hindi man lang nag Hi!"

                cl.direct_answer(thread_id, reply_text)
                logger.info(f"✅ Replied to thread {thread_id} with: {reply_text}")

            time.sleep(5)  # Reduced from 15s to 5s for faster polling

        except Exception as e:
            logger.exception(f"❗ Error in message loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    if login():
        auto_reply_loop()
