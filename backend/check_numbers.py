import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUNAR_API_KEY")

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

response = httpx.get(
    "https://api.voice.hunar.ai/external/v1/numbers/",
    headers=headers,
    timeout=30,
)

print("Status:", response.status_code)
print(response.text)