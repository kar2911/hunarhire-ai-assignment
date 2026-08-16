import os

from dotenv import load_dotenv

load_dotenv()

HUNAR_API_KEY = os.getenv(
    "HUNAR_API_KEY"
)

HUNAR_WEBHOOK_API_KEYS = [
    key.strip()
    for key in os.getenv(
        "HUNAR_WEBHOOK_API_KEYS",
        HUNAR_API_KEY or "",
    ).split(",")
    if key.strip()
]

HUNAR_BASE_URL = (
    "https://api.voice.hunar.ai/external/v1"
)

HUNAR_HIRING_AGENT_ID = (
    "fe6dc9cf-3178-4a44-807e-016a327e9b6f"
)

HUNAR_WEBHOOK_URL = os.getenv(
    "HUNAR_WEBHOOK_URL"
)

if not HUNAR_API_KEY:
    raise ValueError(
        "HUNAR_API_KEY is not configured"
    )

if not HUNAR_WEBHOOK_API_KEYS:
    raise ValueError(
        "HUNAR_WEBHOOK_API_KEYS is not configured"
    )

# Assignment 2 — Outreach (optional; does not affect hiring Voice AI)
HUNAR_OUTREACH_AGENT_ID = os.getenv(
    "HUNAR_OUTREACH_AGENT_ID"
)

HUNAR_OUTREACH_WEBHOOK_URL = os.getenv(
    "HUNAR_OUTREACH_WEBHOOK_URL"
)

# Assignment 2 — People Search (optional; does not affect hiring Voice AI)
PEOPLE_PROVIDER = os.getenv(
    "PEOPLE_PROVIDER",
    "mock",
)

PDL_API_KEY = os.getenv("PDL_API_KEY")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
CORESIGNAL_API_KEY = os.getenv("CORESIGNAL_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")