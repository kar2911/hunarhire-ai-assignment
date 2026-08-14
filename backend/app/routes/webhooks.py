from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Interview


router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"],
)


def to_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@router.post("/hunar")
async def hunar_webhook(
    payload: dict[str, Any],
    db: Session = Depends(get_db),
):
    event_type = payload.get("event_type")
    call_id = payload.get("call_id")

    print("\n========== HUNAR WEBHOOK ==========")
    print("Event:", event_type)
    print("Call ID:", call_id)
    print("===================================\n")

    # We need the call ID to find the interview
    if not call_id:
        return {
            "ok": True,
            "message": "Webhook received without call_id",
        }

    # Find the interview created by /api/interviews/start
    interview = (
        db.query(Interview)
        .filter(Interview.call_id == call_id)
        .first()
    )

    if not interview:
        print(
            f"Interview not found for call_id: {call_id}"
        )

        return {
            "ok": True,
            "message": "Interview not found",
        }

    # Update interview status
    if payload.get("status"):
        interview.status = payload["status"]

    # Extract Hunar structured result
    result = payload.get("result") or {}

    # Scores
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

    # Hiring decision
    interview.recommendation = result.get(
        "recommendation"
    )

    interview.interest_level = result.get(
        "interest_level"
    )

    # Candidate analysis
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

    # Call metadata
    interview.recording_url = payload.get(
        "recording_url"
    )

    interview.duration_seconds = to_float(
        payload.get("duration_seconds")
    )

    # Save everything
    db.commit()
    db.refresh(interview)

    return {
        "ok": True,
        "message": "Interview result stored",
        "interview_id": interview.id,
        "call_id": interview.call_id,
    }