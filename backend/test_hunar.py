import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUNAR_API_KEY")

if not API_KEY:
    raise ValueError("HUNAR_API_KEY is missing")

BASE_URL = "https://api.voice.hunar.ai/external/v1"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

response = httpx.get(
    f"{BASE_URL}/agents/",
    headers=headers,
    timeout=30,
)

print("Status:", response.status_code)
print(response.text)