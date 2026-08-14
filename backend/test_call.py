import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUNAR_API_KEY")

if not API_KEY:
    raise ValueError("HUNAR_API_KEY is missing")

BASE_URL = "https://api.voice.hunar.ai/external/v1"

AGENT_ID = "fe6dc9cf-3178-4a44-807e-016a327e9b6f"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

call_data = {
    "agent_id": AGENT_ID,
    "callee_name": "Karthik",
    "mobile_number": "+919137312854",

    "custom_data": {
        "interview_duration": "10 minutes",

        "job_summary": (
            "We are looking for a software developer with "
            "strong programming and problem-solving skills."
        ),

        "interview_questions": (
            "1. Tell me about yourself and your technical background.\n"
            "2. Tell me about a software project you have worked on.\n"
            "3. What programming languages and technologies are you comfortable with?\n"
            "4. Describe a challenging technical problem you solved.\n"
            "5. Why are you interested in this role?"
        ),

        "company_name": "HunarHire",

        "required_skills": (
            "Python, TypeScript, React, Next.js, SQL"
        ),

        "experience_range": "0-2 years",

        "job_title": "Software Developer",
    },

    "request_id": f"hunarhire-test-{uuid.uuid4()}",
}

response = requests.post(
    f"{BASE_URL}/calls/",
    headers=headers,
    json=call_data,
    timeout=30,
)

print("Status:", response.status_code)
print("Response:")
print(response.text)