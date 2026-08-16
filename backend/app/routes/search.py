from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.people.base import (
    ProviderNotConfiguredError,
    ProviderNotImplementedError,
    ProviderRequestError,
)
from app.services.people.cache import store_people
from app.services.people.extract import extract_search_criteria
from app.services.people.provider import get_people_provider

SEARCH_RESULT_LIMIT = 10
MIN_JOB_DESCRIPTION_LENGTH = 20

SOURCE_LABELS = {
    "serpapi": "Publicly indexed web data",
    "demo": "Demo Data",
    "mock": "Mock provider",
}


router = APIRouter(
    prefix="/api/search",
    tags=["People Search"],
)


class SearchPeopleRequest(BaseModel):
    job_description: str = Field(min_length=1)


@router.post("/people")
def search_people(request: SearchPeopleRequest):
    job_description = request.job_description.strip()

    if len(job_description) < MIN_JOB_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=(
                "Job description must be at least "
                f"{MIN_JOB_DESCRIPTION_LENGTH} characters."
            ),
        )

    try:
        provider = get_people_provider()
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    criteria = extract_search_criteria(job_description)

    try:
        results = provider.search_people(
            criteria,
            limit=SEARCH_RESULT_LIMIT,
        )
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

    results = results[:SEARCH_RESULT_LIMIT]
    store_people(results)

    return {
        "search_criteria": criteria.model_dump(),
        "provider": provider.name,
        "source": SOURCE_LABELS.get(provider.name, provider.name),
        "is_mock": provider.name == "mock",
        "is_demo": provider.name == "demo",
        "total": len(results),
        "results": [person.model_dump() for person in results],
    }
