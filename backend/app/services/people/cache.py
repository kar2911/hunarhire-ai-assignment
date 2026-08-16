from app.services.people.base import NormalizedPerson
from app.services.people.phone import PHONE_SOURCE_RECRUITER

# Process-local cache so profile pages can load after search
# without mixing into Assignment 1 Candidate rows.
_PERSON_CACHE: dict[str, NormalizedPerson] = {}
_ENRICHED_IDS: set[str] = set()


def store_people(people: list[NormalizedPerson]) -> None:
    for person in people:
        _PERSON_CACHE[person.id] = person


def get_cached_person(person_id: str) -> NormalizedPerson | None:
    return _PERSON_CACHE.get(person_id)


def is_enriched(person_id: str) -> bool:
    return person_id in _ENRICHED_IDS


def mark_enriched(person_id: str) -> None:
    _ENRICHED_IDS.add(person_id)


def clear_people_cache() -> None:
    _PERSON_CACHE.clear()
    _ENRICHED_IDS.clear()


def update_cached_phone(
    person_id: str,
    phone: str,
) -> NormalizedPerson | None:
    person = _PERSON_CACHE.get(person_id)

    if person is None:
        return None

    updated = person.model_copy(
        update={
            "phone": phone,
            "phone_source": PHONE_SOURCE_RECRUITER,
        }
    )
    _PERSON_CACHE[person_id] = updated

    return updated
