from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Outreach(Base):
    __tablename__ = "outreach"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    person_id = Column(
        String(255),
        nullable=False,
        index=True,
    )

    person_name = Column(
        String(255),
        nullable=True,
    )

    job_title = Column(
        String(255),
        nullable=True,
    )

    phone_number = Column(
        String(30),
        nullable=False,
    )

    call_id = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )

    request_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    status = Column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True,
    )

    lifecycle_status = Column(
        String(50),
        default="PENDING",
        nullable=False,
    )

    result = Column(
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

    answered_by = Column(
        String(100),
        nullable=True,
    )

    engagement_status = Column(
        String(100),
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
