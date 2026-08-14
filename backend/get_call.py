import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUNAR_API_KEY")

if not API_KEY:
    raise ValueError("HUNAR_API_KEY is missing")

CALL_ID = "3fdecf37-8c1f-4922-bfc5-9627b764d3b0"

URL = f"https://api.voice.hunar.ai/external/v1/calls/{CALL_ID}/"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30,
)

print("Status:", response.status_code)
print("Response:")
print(response.text)