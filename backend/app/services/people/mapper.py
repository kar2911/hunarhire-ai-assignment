from typing import Any

from app.services.people.base import (
    EducationItem,
    ExperienceItem,
    NormalizedPerson,
)


def optional_str(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def string_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        items = [part.strip() for part in value.split(",")]
        return [item for item in items if item]

    if isinstance(value, list):
        items = [optional_str(item) for item in value]
        return [item for item in items if item]

    return []


def make_person_id(provider: str, provider_id: str) -> str:
    return f"{provider}:{provider_id}"


def parse_person_id(person_id: str) -> tuple[str, str]:
    if ":" not in person_id:
        return ("unknown", person_id)

    provider, provider_id = person_id.split(":", 1)
    return (provider, provider_id)


def to_experience_item(raw: dict[str, Any] | None) -> ExperienceItem:
    raw = raw or {}

    return ExperienceItem(
        title=optional_str(raw.get("title")),
        company=optional_str(raw.get("company")),
        location=optional_str(raw.get("location")),
        start_date=optional_str(raw.get("start_date")),
        end_date=optional_str(raw.get("end_date")),
        description=optional_str(raw.get("description")),
    )


def to_education_item(raw: dict[str, Any] | None) -> EducationItem:
    raw = raw or {}

    return EducationItem(
        school=optional_str(raw.get("school")),
        degree=optional_str(raw.get("degree")),
        field=optional_str(raw.get("field")),
        start_date=optional_str(raw.get("start_date")),
        end_date=optional_str(raw.get("end_date")),
    )


def to_normalized_person(
    provider: str,
    provider_id: str,
    raw: dict[str, Any],
) -> NormalizedPerson:
    """
    Map a loosely-shaped dict onto the internal person model.

    Real PDL/Apollo/Coresignal adapters should convert provider JSON
    into this dict (or call this helper) so the API never returns
    raw provider payloads.
    """

    first_name = optional_str(raw.get("first_name"))
    last_name = optional_str(raw.get("last_name"))
    full_name = optional_str(raw.get("full_name"))

    if not full_name:
        full_name = " ".join(
            part for part in [first_name, last_name] if part
        ) or None

    experience_raw = raw.get("experience") or []
    education_raw = raw.get("education") or []

    return NormalizedPerson(
        id=make_person_id(provider, provider_id),
        provider=provider,
        provider_id=provider_id,
        full_name=full_name,
        first_name=first_name,
        last_name=last_name,
        job_title=optional_str(raw.get("job_title")),
        company_name=optional_str(raw.get("company_name")),
        company_website=optional_str(raw.get("company_website")),
        location=optional_str(raw.get("location")),
        linkedin_url=optional_str(raw.get("linkedin_url")),
        skills=string_list(raw.get("skills")),
        headline=optional_str(raw.get("headline")),
        summary=optional_str(raw.get("summary")),
        email=optional_str(raw.get("email")),
        phone=optional_str(raw.get("phone")),
        phone_source=optional_str(raw.get("phone_source")),
        public_phone=optional_str(raw.get("public_phone")),
        experience=[
            to_experience_item(item)
            for item in experience_raw
            if isinstance(item, dict)
        ],
        education=[
            to_education_item(item)
            for item in education_raw
            if isinstance(item, dict)
        ],
    )
