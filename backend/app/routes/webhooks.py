import base64
import hashlib
import hmac
import json
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import HUNAR_WEBHOOK_API_KEYS
from app.database import get_db
from app.models import Interview


router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"],
)


MAX_WEBHOOK_AGE_SECONDS = 300


def verify_hunar_signature(
    body: bytes,
    timestamp: str,
    signature_header: str,
    api_keys: list[str],
) -> bool:
    """
    Verify Hunar webhook signature.

    Hunar signs:
        timestamp + "." + raw_request_body

    using HMAC-SHA256 with the API key.
    """

    if not timestamp or not signature_header:
        return False

    try:
        timestamp_int = int(timestamp)
    except ValueError:
        return False

    # Reject stale/future requests
    current_time = int(time.time())

    if abs(current_time - timestamp_int) > MAX_WEBHOOK_AGE_SECONDS:
        return False

    signed_payload = (
        timestamp.encode("utf-8")
        + b"."
        + body
    )

    # Hunar may provide multiple signatures separated by commas.
    provided_signatures = [
        value.strip()
        for value in signature_header.split(",")
        if value.strip()
    ]

    for api_key in api_keys:
        expected_digest = hmac.new(
            api_key.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).digest()

        expected_signature = base64.b64encode(
            expected_digest
        ).decode("utf-8")

        for provided_signature in provided_signatures:
            if hmac.compare_digest(
                expected_signature,
                provided_signature,
            ):
                return True

    return False


def to_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@router.post("/hunar")
async def hunar_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.body()

    timestamp = request.headers.get(
        "X-Hunar-Timestamp"
    )

    signature = request.headers.get(
        "X-Hunar-Signature"
    )

    if not verify_hunar_signature(
        body=body,
        timestamp=timestamp or "",
        signature_header=signature or "",
        api_keys=HUNAR_WEBHOOK_API_KEYS,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    try:
        payload = json.loads(
            body.decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        )

    event_type = payload.get("event_type")
    call_id = payload.get("call_id")

    print("\n========== HUNAR WEBHOOK ==========")
    print("Event:", event_type)
    print("Call ID:", call_id)
    print("===================================\n")

    if not call_id:
        return {
            "ok": True,
            "message": "Webhook received without call_id",
        }

    interview = (
        db.query(Interview)
        .filter(Interview.call_id == call_id)
        .first()
    )

    if not interview:
        return {
            "ok": True,
            "message": "Interview not found",
        }

    # Idempotency:
    # If the same terminal event is delivered again,
    # simply acknowledge it without reprocessing.
    if (
        interview.status == "COMPLETED"
        and payload.get("status") == "COMPLETED"
    ):
        return {
            "ok": True,
            "message": "Webhook already processed",
            "interview_id": interview.id,
            "call_id": interview.call_id,
        }

    if payload.get("status"):
        interview.status = payload["status"]

    result = payload.get("result") or {}

    interview.overall_score = to_float(
        result.get("overall_score")
    )

    interview.technical_score = to_float(
        result.get("technical_score")
    )

    interview.communication_score = to_float(
        result.get("communication_score")
    )

    interview.experience_score = to_float(
        result.get("experience_score")
    )

    interview.problem_solving_score = to_float(
        result.get("problem_solving_score")
    )

    interview.role_fit_score = to_float(
        result.get("role_fit_score")
    )

    interview.recommendation = result.get(
        "recommendation"
    )

    interview.interest_level = result.get(
        "interest_level"
    )

    interview.summary = result.get(
        "candidate_summary"
    )

    interview.strengths = result.get(
        "strengths"
    )

    interview.concerns = result.get(
        "concerns"
    )

    interview.next_steps = result.get(
        "next_steps"
    )

    interview.transcript = result.get(
        "conversation_transcript"
    )

    interview.recording_url = payload.get(
        "recording_url"
    )

    interview.duration_seconds = to_float(
        payload.get("duration_seconds")
    )

    db.commit()
    db.refresh(interview)

    return {
        "ok": True,
        "message": "Interview result stored",
        "interview_id": interview.id,
        "call_id": interview.call_id,
    }