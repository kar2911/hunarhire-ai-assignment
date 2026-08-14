from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    mobile_number = Column(
        String(30),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    interviews = relationship(
        "Interview",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    call_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    job_title = Column(
        String(255),
        nullable=False,
    )

    status = Column(
        String(50),
        default="NOT_STARTED",
        nullable=False,
        index=True,
    )

    overall_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    role_fit_score = Column(Float, nullable=True)

    recommendation = Column(
        String(100),
        nullable=True,
    )

    interest_level = Column(
        String(100),
        nullable=True,
    )

    summary = Column(
        Text,
        nullable=True,
    )

    strengths = Column(
        Text,
        nullable=True,
    )

    concerns = Column(
        Text,
        nullable=True,
    )

    next_steps = Column(
        Text,
        nullable=True,
    )

    transcript = Column(
        Text,
        nullable=True,
    )

    recording_url = Column(
        Text,
        nullable=True,
    )

    duration_seconds = Column(
        Float,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    candidate = relationship(
        "Candidate",
        back_populates="interviews",
    )