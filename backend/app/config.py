import os

from dotenv import load_dotenv

load_dotenv()

HUNAR_API_KEY = os.getenv("HUNAR_API_KEY")

HUNAR_BASE_URL = "https://api.voice.hunar.ai/external/v1"

HUNAR_HIRING_AGENT_ID = (
    "fe6dc9cf-3178-4a44-807e-016a327e9b6f"
)

HUNAR_WEBHOOK_URL = os.getenv("HUNAR_WEBHOOK_URL")

if not HUNAR_API_KEY:
    raise ValueError("HUNAR_API_KEY is not configured")

if not HUNAR_WEBHOOK_URL:
    raise ValueError("HUNAR_WEBHOOK_URL is not configured")