import uuid

import requests

from app.config import (
    HUNAR_API_KEY,
    HUNAR_BASE_URL,
    HUNAR_OUTREACH_WEBHOOK_URL,
)


class OutreachHunarError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def generate_outreach_request_id() -> str:
    return f"outreach-{uuid.uuid4()}"


def create_outreach_call(
    *,
    agent_id: str,
    callee_name: str,
    mobile_number: str,
    custom_data: dict,
    request_id: str,
) -> dict:
    headers = {
        "X-API-Key": HUNAR_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "agent_id": agent_id,
        "callee_name": callee_name,
        "mobile_number": mobile_number,
        "custom_data": custom_data,
        "request_id": request_id,
    }

    webhook_url = (HUNAR_OUTREACH_WEBHOOK_URL or "").strip()

    if webhook_url:
        payload["callback_config"] = {
            "call_status_callback_url": webhook_url,
            "call_recording_callback_url": webhook_url,
            "call_result_callback_url": webhook_url,
            "call_summary_callback_url": webhook_url,
        }

    try:
        response = requests.post(
            f"{HUNAR_BASE_URL}/calls/",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException:
        raise OutreachHunarError(
            "Unable to start the outreach call.",
            status_code=502,
        ) from None

    if response.status_code >= 400:
        mapped_status = 422 if response.status_code == 422 else 502

        if response.status_code in {400, 401, 403}:
            mapped_status = 502

        raise OutreachHunarError(
            "Unable to start the outreach call.",
            status_code=mapped_status,
        )

    try:
        return response.json()
    except ValueError:
        raise OutreachHunarError(
            "Unable to start the outreach call.",
            status_code=502,
        ) from None
