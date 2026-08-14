from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Interview


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/interviews")
def list_interviews(
    db: Session = Depends(get_db),
):
    interviews = (
        db.query(Interview)
        .order_by(Interview.created_at.desc())
        .all()
    )

    return [
        {
            "id": interview.id,
            "candidate_id": interview.candidate_id,
            "call_id": interview.call_id,
            "job_title": interview.job_title,
            "status": interview.status,
            "overall_score": interview.overall_score,
            "recommendation": interview.recommendation,
            "interest_level": interview.interest_level,
            "created_at": interview.created_at,
        }
        for interview in interviews
    ]


@router.get("/interviews/{interview_id}")
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):
    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    candidate = interview.candidate

    return {
        "id": interview.id,
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "mobile_number": candidate.mobile_number,
        },
        "call_id": interview.call_id,
        "job_title": interview.job_title,
        "status": interview.status,
        "scores": {
            "overall": interview.overall_score,
            "technical": interview.technical_score,
            "communication": interview.communication_score,
            "experience": interview.experience_score,
            "problem_solving": interview.problem_solving_score,
            "role_fit": interview.role_fit_score,
        },
        "recommendation": interview.recommendation,
        "interest_level": interview.interest_level,
        "summary": interview.summary,
        "strengths": interview.strengths,
        "concerns": interview.concerns,
        "next_steps": interview.next_steps,
        "transcript": interview.transcript,
        "recording_url": interview.recording_url,
        "duration_seconds": interview.duration_seconds,
        "created_at": interview.created_at,
        "updated_at": interview.updated_at,
    }