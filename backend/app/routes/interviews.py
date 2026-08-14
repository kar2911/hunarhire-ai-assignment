from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import (
    HUNAR_HIRING_AGENT_ID,
    HUNAR_WEBHOOK_URL,
)
from app.database import get_db
from app.models import Candidate, Interview
from app.services.hunar import HunarService


router = APIRouter(
    prefix="/api/interviews",
    tags=["Interviews"],
)


class StartInterviewRequest(BaseModel):
    candidate_name: str = Field(min_length=1)
    mobile_number: str = Field(min_length=10)

    job_title: str
    job_summary: str
    company_name: str
    required_skills: str
    experience_range: str
    interview_duration: str
    interview_questions: str


@router.post("/start")
def start_interview(
    request: StartInterviewRequest,
    db: Session = Depends(get_db),
):
    hunar = HunarService()

    custom_data = {
        "job_title": request.job_title,
        "job_summary": request.job_summary,
        "company_name": request.company_name,
        "required_skills": request.required_skills,
        "experience_range": request.experience_range,
        "interview_duration": request.interview_duration,
        "interview_questions": request.interview_questions,
    }

    try:
        # 1. Create candidate in our database
        candidate = Candidate(
            name=request.candidate_name,
            mobile_number=request.mobile_number,
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        # 2. Create the Hunar AI call
        call = hunar.create_call(
            agent_id=HUNAR_HIRING_AGENT_ID,
            candidate_name=request.candidate_name,
            mobile_number=request.mobile_number,
            custom_data=custom_data,
            callback_url=HUNAR_WEBHOOK_URL,
        )

        # 3. Save the interview in our database
        interview = Interview(
            candidate_id=candidate.id,
            call_id=call["id"],
            job_title=request.job_title,
            status=call.get("status", "NOT_STARTED"),
        )

        db.add(interview)
        db.commit()
        db.refresh(interview)

        return {
            "success": True,
            "message": "AI interview started",
            "candidate_id": candidate.id,
            "interview_id": interview.id,
            "call": call,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc