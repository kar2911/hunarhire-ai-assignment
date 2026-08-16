import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import HUNAR_WEBHOOK_API_KEYS
from app.database import get_db
from app.outreach_models import Outreach, utc_now
from app.routes.webhooks import verify_hunar_signature


router = APIRouter(
    prefix="/api/webhooks",
    tags=["Outreach Webhooks"],
)


def to_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def engagement_from_result(result: dict[str, Any]) -> str | None:
    for key in (
        "open_to_opportunities",
        "engagement_status",
        "interested",
    ):
        value = result.get(key)

        if value is None:
            continue

        text = str(value).strip()

        if text:
            return text

    return None


@router.post("/hunar-outreach")
async def hunar_outreach_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.body()

    timestamp = request.headers.get("X-Hunar-Timestamp")
    signature = request.headers.get("X-Hunar-Signature")

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
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        )

    event_type = payload.get("event_type")
    call_id = payload.get("call_id")
    request_id = payload.get("request_id")

    outreach = None

    if call_id:
        outreach = (
            db.query(Outreach)
            .filter(Outreach.call_id == call_id)
            .first()
        )

    if outreach is None and request_id:
        outreach = (
            db.query(Outreach)
            .filter(Outreach.request_id == request_id)
            .first()
        )

    if outreach is None:
        return {
            "ok": True,
            "message": "Outreach not found",
        }

    if (
        event_type == "call_summary"
        and outreach.status == "COMPLETED"
        and payload.get("status") == "COMPLETED"
    ):
        return {
            "ok": True,
            "message": "Webhook already processed",
            "outreach_id": outreach.id,
            "call_id": outreach.call_id,
        }

    if event_type == "call_status_updated":
        if payload.get("status"):
            outreach.status = payload["status"]

        if payload.get("lifecycle_status"):
            outreach.lifecycle_status = payload["lifecycle_status"]

        if payload.get("answered_by"):
            outreach.answered_by = payload["answered_by"]

        duration = to_float(payload.get("duration_seconds"))

        if duration is not None:
            outreach.duration_seconds = duration

    elif event_type == "call_recording_done":
        if payload.get("recording_url"):
            outreach.recording_url = payload["recording_url"]

    elif event_type == "call_result_done":
        result = payload.get("result") or {}

        if result:
            outreach.result = json.dumps(result)
            outreach.engagement_status = engagement_from_result(result)

    elif event_type == "call_summary":
        if payload.get("status"):
            outreach.status = payload["status"]

        if payload.get("lifecycle_status"):
            outreach.lifecycle_status = payload["lifecycle_status"]

        if payload.get("answered_by"):
            outreach.answered_by = payload["answered_by"]

        duration = to_float(payload.get("duration_seconds"))

        if duration is not None:
            outreach.duration_seconds = duration

        if payload.get("recording_url"):
            outreach.recording_url = payload["recording_url"]

        result = payload.get("result") or {}

        if result:
            outreach.result = json.dumps(result)
            outreach.engagement_status = engagement_from_result(result)

    outreach.updated_at = utc_now()
    db.commit()
    db.refresh(outreach)

    return {
        "ok": True,
        "message": "Outreach updated",
        "outreach_id": outreach.id,
        "call_id": outreach.call_id,
    }
