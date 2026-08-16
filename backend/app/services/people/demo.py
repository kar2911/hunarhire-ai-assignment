import json
from pathlib import Path

from app.services.people.base import (
    NormalizedPerson,
    SearchCriteria,
)
from app.services.people.mapper import to_normalized_person

DEMO_RECORDS_PATH = Path(__file__).with_name("demo_records.json")

RELATED_TITLES = {
    "forward deployed engineer": {"forward deployed engineer"},
    "testing engineer": {"testing engineer"},
    "devops engineer": {"devops engineer"},
    "python developer": {"python developer", "software developer"},
    "full stack developer": {"full stack developer", "software developer"},
    "software developer": {
        "software developer",
        "python developer",
        "full stack developer",
    },
}


class DemoPeopleProvider:
    """
    Isolated Assignment 2 demonstration provider.

    Records are Demo Data, not SerpApi or LinkedIn. Does not write
    Candidate or Interview rows.
    """

    name = "demo"

    def search_people(
        self,
        criteria: SearchCriteria,
        limit: int = 10,
    ) -> list[NormalizedPerson]:
        people = load_demo_people()
        ranked = rank_demo_people(people, criteria)
        return ranked[: min(max(limit, 0), 15)]

    def get_person(self, person_id: str) -> NormalizedPerson | None:
        if not person_id.startswith("demo:"):
            return None

        for person in load_demo_people():
            if person.id == person_id:
                return person

        return None


def load_demo_people() -> list[NormalizedPerson]:
    if not DEMO_RECORDS_PATH.exists():
        return []

    try:
        payload = json.loads(DEMO_RECORDS_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(payload, list):
        return []

    people: list[NormalizedPerson] = []

    for index, raw in enumerate(payload):
        if not isinstance(raw, dict):
            continue

        person = record_to_person(raw, index)

        if person is not None:
            people.append(person)

    return people


def record_to_person(raw: dict, index: int) -> NormalizedPerson | None:
    record_id = str(raw.get("id") or f"record-{index + 1}").strip()

    if not record_id or record_id.startswith("replace-me"):
        return None

    name = (raw.get("name") or "").strip()

    if not name or name.lower().startswith("replace with"):
        return None

    first_name = None
    last_name = None
    parts = name.split()

    if parts:
        first_name = parts[0]
        last_name = " ".join(parts[1:]) or None

    experience = raw.get("experience") or []
    education = raw.get("education") or []
    phone_source = (raw.get("phone_source") or "demo_data").strip()
    phone = raw.get("phone")
    public_phone = None

    if phone_source == "public_web":
        public_phone = raw.get("public_phone") or phone

    return to_normalized_person(
        provider="demo",
        provider_id=record_id,
        raw={
            "full_name": name,
            "first_name": first_name,
            "last_name": last_name,
            "job_title": raw.get("current_title") or raw.get("job_title"),
            "company_name": raw.get("company"),
            "location": raw.get("location"),
            "linkedin_url": raw.get("linkedin_url"),
            "headline": raw.get("headline"),
            "summary": raw.get("summary"),
            "email": raw.get("email"),
            "phone": phone,
            "public_phone": public_phone,
            "phone_source": phone_source,
            "skills": raw.get("skills") or [],
            "experience": experience if isinstance(experience, list) else [],
            "education": education if isinstance(education, list) else [],
        },
    )


def normalize_title(value: str | None) -> str:
    return " ".join((value or "").lower().split())


def requested_title_family(criteria: SearchCriteria) -> set[str]:
    title = normalize_title(criteria.job_title)

    if not title:
        return set()

    if title in RELATED_TITLES:
        return RELATED_TITLES[title]

    for key, family in RELATED_TITLES.items():
        if key in title or title in key:
            return family

    return {title}


def rank_demo_people(
    people: list[NormalizedPerson],
    criteria: SearchCriteria,
) -> list[NormalizedPerson]:
    scored: list[tuple[int, NormalizedPerson]] = []
    family = requested_title_family(criteria)
    wanted_skills = [skill.lower() for skill in criteria.skills[:5]]
    location = (criteria.location or "").lower()

    for person in people:
        person_title = normalize_title(person.job_title)
        person_skills = [skill.lower() for skill in person.skills]
        score = 0

        if family and person_title in family:
            if criteria.job_title and person_title == normalize_title(
                criteria.job_title
            ):
                score += 8
            else:
                score += 4

        skill_hits = sum(1 for skill in wanted_skills if skill in person_skills)
        score += skill_hits * 3

        if location and person.location and location in person.location.lower():
            score += 1

        title_ok = bool(family) and person_title in family
        skills_ok = skill_hits >= 2

        if not title_ok and not skills_ok:
            continue

        if score <= 0:
            continue

        scored.append((score, person))

    scored.sort(key=lambda item: (-item[0], item[1].full_name or ""))
    return [person for _score, person in scored]
