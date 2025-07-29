import os
import logging
import asyncio
from dotenv import load_dotenv
from instagrapi import Client
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()
ACCOUNT_USERNAME = os.getenv("ACCOUNT_USERNAME")
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

# Instagram client and state
cl = Client()
reply_task = None
last_replied_message_ids = {}

def login():
    """Login with session persistence"""
    try:
        if os.path.exists("session.json"):
            cl.load_settings("session.json")
            logger.info("🔄 Loaded session from file")

        cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
        cl.dump_settings("session.json")
        logger.info("✅ Logged in as %s", cl.username)
        return True
    except Exception as e:
        logger.error("❌ Login failed: %s", e)
        return False

async def auto_reply_loop():
    logger.info("💬 Starting auto-reply loop...")
    while True:
        try:
            threads = cl.direct_threads(selected_filter="unread", amount=20)
            logger.info(f"📥 Found {len(threads)} unread threads.")
            
            for thread in threads:
                thread_id = thread.id
                messages = cl.direct_messages(thread_id, amount=1)

                if not messages:
                    continue

                message = messages[0]
                message_text = (message.text or "").strip().lower()

                if message.user_id == cl.user_id:
                    continue

                last_id = last_replied_message_ids.get(thread_id)
                if message.id == last_id:
                    continue

                logger.info("📩 New message from %s: %s", message.user_id, message_text)

                if message_text == "hi":
                    reply_text = "Hello! Welcome sa aking business account. How can I help you?"
                else:
                    reply_text = "Hindi man lang nag Hi!"

                cl.direct_answer(thread_id, reply_text)
                last_replied_message_ids[thread_id] = message.id
                logger.info("✅ Replied to thread %s", thread_id)

            await asyncio.sleep(5)
        except Exception as e:
            logger.error("❗ Error in auto-reply loop: %s", e)
            await asyncio.sleep(10)

# FastAPI startup/shutdown management
@asynccontextmanager
async def lifespan(app: FastAPI):
    global reply_task
    if login():
        reply_task = asyncio.create_task(auto_reply_loop())
    yield
    if reply_task:
        reply_task.cancel()
        try:
            await reply_task
        except asyncio.CancelledError:
            logger.info("🛑 Auto-reply loop cancelled.")

app.router.lifespan_context = lifespan

# Routes
@app.get("/", response_class=PlainTextResponse)
def root():
    return "🤖 Instagram auto-reply bot is running!"

@app.get("/health", response_class=PlainTextResponse)
def health():
    if cl.username:
        return f"✅ Logged in as: {cl.username}"
    return "❌ Not logged in"
