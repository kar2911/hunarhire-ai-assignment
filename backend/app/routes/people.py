import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.people.base import (
    ProviderNotConfiguredError,
    ProviderNotImplementedError,
    ProviderRequestError,
)
from app.services.people.cache import (
    get_cached_person,
    is_enriched,
    mark_enriched,
    store_people,
    update_cached_phone,
)
from app.services.people.provider import get_people_provider


router = APIRouter(
    prefix="/api/people",
    tags=["People Search"],
)


class SavePhoneRequest(BaseModel):
    phone: str = Field(min_length=1)


def normalize_recruiter_phone(raw: str) -> str:
    cleaned = raw.strip()

    if not cleaned:
        raise HTTPException(
            status_code=422,
            detail="Enter a valid phone number.",
        )

    if not re.fullmatch(r"\+?[0-9][0-9\s\-()]{8,24}", cleaned):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid phone number.",
        )

    digits = re.sub(r"\D", "", cleaned)

    if len(digits) < 10:
        raise HTTPException(
            status_code=422,
            detail="Enter a valid phone number with at least 10 digits.",
        )

    if cleaned.startswith("+"):
        return "+" + digits

    return digits


def maybe_enrich_person(person):
    if is_enriched(person.id):
        return person

    if person.provider == "demo":
        mark_enriched(person.id)
        return person

    try:
        provider = get_people_provider()
    except ValueError:
        mark_enriched(person.id)
        return person

    enrich = getattr(provider, "enrich_person", None)

    if not callable(enrich):
        mark_enriched(person.id)
        return person

    try:
        person = enrich(person)
    except (ProviderNotConfiguredError, ProviderRequestError):
        pass

    mark_enriched(person.id)
    store_people([person])
    return person


@router.put("/{person_id}/phone")
def save_person_phone(person_id: str, request: SavePhoneRequest):
    phone = normalize_recruiter_phone(request.phone)
    person = update_cached_phone(person_id, phone)

    if person is None:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    return person.model_dump()


@router.get("/{person_id}")
def get_person(person_id: str):
    cached = get_cached_person(person_id)

    if cached is not None:
        return maybe_enrich_person(cached).model_dump()

    try:
        provider = get_people_provider()
        person = provider.get_person(person_id)
    except ProviderNotConfiguredError:
        raise HTTPException(
            status_code=503,
            detail="People search provider is not configured.",
        )
    except ProviderNotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail=str(exc),
        ) from exc
    except ProviderRequestError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    if person is None:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    store_people([person])
    return maybe_enrich_person(person).model_dump()
