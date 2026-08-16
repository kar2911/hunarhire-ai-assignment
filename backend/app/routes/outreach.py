import json
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import HUNAR_OUTREACH_AGENT_ID
from app.database import get_db
from app.outreach_models import Outreach, utc_now
from app.services.outreach_hunar import (
    OutreachHunarError,
    create_outreach_call,
    generate_outreach_request_id,
)
from app.services.people.cache import get_cached_person

OUTREACH_QUESTIONS = (
    "Identify yourself clearly before any screening questions. "
    "You are an AI recruitment assistant calling on behalf of Hunar.ai. "
    "You represent Hunar.ai as the recruiter. Do not say Hunar.ai is the "
    "candidate's current employer, and do not treat the candidate's current "
    "company as the hiring company. Do not invent a client or company name.\n"
    "Open approximately like this:\n"
    "\"Hi, am I speaking with [Candidate Name]? "
    "I'm an AI recruitment assistant calling on behalf of Hunar.ai. "
    "I'm reaching out regarding a {role_title} opportunity. "
    "Is this a good time to speak?\"\n"
    "If they agree, continue naturally and concisely:\n"
    "1. Ask whether they are open to exploring this opportunity.\n"
    "2. Ask their current or expected notice period.\n"
    "3. Ask their salary expectation.\n"
    "4. Ask whether they are interested in proceeding.\n"
    "Capture results as open_to_opportunities, notice_period, and "
    "salary_expectation. Keep the conversation professional and concise."
)

E164_RE = re.compile(r"^\+[1-9]\d{9,14}$")


router = APIRouter(
    prefix="/api/outreach",
    tags=["Outreach"],
)


class StartOutreachRequest(BaseModel):
    person_id: str = Field(min_length=1)
    phone: str = Field(min_length=1)


def normalize_e164(phone: str) -> str:
    cleaned = re.sub(r"[\s\-()]", "", phone.strip())

    if not E164_RE.fullmatch(cleaned):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid E.164 phone number.",
        )

    return cleaned


def serialize_outreach(outreach: Outreach) -> dict:
    result = outreach.result

    if result:
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            pass

    return {
        "id": outreach.id,
        "person_id": outreach.person_id,
        "person_name": outreach.person_name,
        "job_title": outreach.job_title,
        "phone_number": outreach.phone_number,
        "call_id": outreach.call_id,
        "request_id": outreach.request_id,
        "status": outreach.status,
        "lifecycle_status": outreach.lifecycle_status,
        "result": result,
        "recording_url": outreach.recording_url,
        "duration_seconds": outreach.duration_seconds,
        "answered_by": outreach.answered_by,
        "engagement_status": outreach.engagement_status,
        "created_at": outreach.created_at,
        "updated_at": outreach.updated_at,
    }


@router.post("/call")
def start_outreach_call(
    request: StartOutreachRequest,
    db: Session = Depends(get_db),
):
    agent_id = (HUNAR_OUTREACH_AGENT_ID or "").strip()

    if not agent_id:
        raise HTTPException(
            status_code=503,
            detail="Outreach agent is not configured.",
        )

    person = get_cached_person(request.person_id)

    if person is None:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    phone = normalize_e164(request.phone)
    request_id = generate_outreach_request_id()
    callee_name = person.full_name or "Candidate"
    role_title = person.job_title or "the role"

    outreach = Outreach(
        person_id=person.id,
        person_name=person.full_name,
        job_title=person.job_title,
        phone_number=phone,
        request_id=request_id,
        status="PENDING",
        lifecycle_status="PENDING",
    )

    db.add(outreach)
    db.commit()
    db.refresh(outreach)

    try:
        call = create_outreach_call(
            agent_id=agent_id,
            callee_name=callee_name,
            mobile_number=phone,
            custom_data={
                "role_title": role_title,
                "questions": OUTREACH_QUESTIONS,
            },
            request_id=request_id,
        )
    except OutreachHunarError as exc:
        outreach.status = "FAILED"
        outreach.lifecycle_status = "FAILED"
        outreach.updated_at = utc_now()
        db.commit()

        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc

    outreach.call_id = call.get("id")
    outreach.status = call.get("status") or "NOT_STARTED"
    outreach.lifecycle_status = (
        call.get("lifecycle_status") or outreach.status
    )
    outreach.updated_at = utc_now()
    db.commit()
    db.refresh(outreach)

    return {
        "id": outreach.id,
        "call_id": outreach.call_id,
        "request_id": outreach.request_id,
        "status": outreach.status,
        "lifecycle_status": outreach.lifecycle_status,
    }


@router.get("")
def list_outreach(db: Session = Depends(get_db)):
    rows = (
        db.query(Outreach)
        .order_by(Outreach.created_at.desc())
        .all()
    )

    return [serialize_outreach(row) for row in rows]


@router.get("/{outreach_id}")
def get_outreach(
    outreach_id: int,
    db: Session = Depends(get_db),
):
    outreach = (
        db.query(Outreach)
        .filter(Outreach.id == outreach_id)
        .first()
    )

    if outreach is None:
        raise HTTPException(
            status_code=404,
            detail="Outreach not found",
        )

    return serialize_outreach(outreach)
