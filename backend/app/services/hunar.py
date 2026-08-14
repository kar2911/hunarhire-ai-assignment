import uuid
import requests

from app.config import HUNAR_API_KEY, HUNAR_BASE_URL


class HunarService:

    def __init__(self):
        self.headers = {
            "X-API-Key": HUNAR_API_KEY,
            "Content-Type": "application/json",
        }

    def list_agents(self):
        response = requests.get(
            f"{HUNAR_BASE_URL}/agents/",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_agent(self, agent_id: str):
        response = requests.get(
            f"{HUNAR_BASE_URL}/agents/{agent_id}/",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def create_call(
        self,
        agent_id: str,
        candidate_name: str,
        mobile_number: str,
        custom_data: dict,
        callback_url: str | None = None,
    ):
        call_data = {
            "agent_id": agent_id,
            "callee_name": candidate_name,
            "mobile_number": mobile_number,
            "custom_data": custom_data,
            "request_id": f"hunarhire-{uuid.uuid4()}",
        }

        if callback_url:
            call_data["callback_config"] = {
                "call_summary_callback_url": callback_url
            }

        response = requests.post(
            f"{HUNAR_BASE_URL}/calls/",
            headers=self.headers,
            json=call_data,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_call(self, call_id: str):
        response = requests.get(
            f"{HUNAR_BASE_URL}/calls/{call_id}/",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()