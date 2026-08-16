import re
from typing import Any

from app.services.people.base import NormalizedPerson

PHONE_SOURCE_PUBLIC_WEB = "public_web"
PHONE_SOURCE_RECRUITER = "recruiter_provided"

# Formatted public numbers only; do not invent missing digits.
PHONE_CANDIDATE_RE = re.compile(
    r"(?<!\w)(?:\+|00)?(?:\(?\d[\d\s\-().]{8,18}\d)(?!\w)"
)

SWITCHBOARD_RE = re.compile(
    r"\b("
    r"switchboard|reception|receptionist|front desk|toll[\s\-]?free|"
    r"customer (?:care|service|support)|helpline|call centre|call center|"
    r"head office|main office|main line|ivr|sales (?:enquiry|inquiry|hotline)|"
    r"contact us|phone directory"
    r")\b",
    re.IGNORECASE,
)

TOLL_FREE_RE = re.compile(
    r"^(?:\+?1)?(?:800|888|877|866|855|844|833)|^(?:\+?91)?(?:1800|1860)"
)

INDIA_LOCATION_RE = re.compile(
    r"\b(india|bharat|bengaluru|bangalore|hyderabad|mumbai|delhi|"
    r"chennai|pune|gurgaon|gurugram|noida|kolkata|kerala|karnataka|"
    r"telangana|maharashtra|ahmedabad|jaipur)\b",
    re.IGNORECASE,
)

US_LOCATION_RE = re.compile(
    r"\b(united states|\busa\b|\bu\.s\.a?\b|california|new york|"
    r"seattle|austin|texas|san francisco|chicago|boston)\b",
    re.IGNORECASE,
)

PHONE_FIELD_KEYS = {
    "phone",
    "telephone",
    "tel",
    "phone_number",
    "phonenumber",
    "work_phone",
    "business_phone",
    "office_phone",
    "office_number",
    "mobile",
}


def discover_public_professional_phone(
    person: NormalizedPerson,
    payload: dict[str, Any],
) -> str | None:
    """
    Return a single E.164 professional number only when public SERP
    evidence clearly ties it to this person. Otherwise None.
    """

    if not person.full_name and not (
        person.first_name and person.last_name
    ):
        return None

    candidates: list[str] = []

    for result in iter_search_results(payload):
        extracted = phones_from_associated_result(person, result)
        candidates.extend(extracted)

    unique = list(dict.fromkeys(candidates))

    if len(unique) != 1:
        return None

    return unique[0]


def iter_search_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    organic = payload.get("organic_results") or []

    if isinstance(organic, list):
        results.extend(item for item in organic if isinstance(item, dict))

    knowledge_graph = payload.get("knowledge_graph")

    if isinstance(knowledge_graph, dict):
        results.append(knowledge_graph)

    answer_box = payload.get("answer_box")

    if isinstance(answer_box, dict):
        results.append(answer_box)

    return results


def phones_from_associated_result(
    person: NormalizedPerson,
    result: dict[str, Any],
) -> list[str]:
    title = stringify(result.get("title"))
    snippet = stringify(result.get("snippet"))
    association_text = " ".join(
        part
        for part in [
            title,
            snippet,
            stringify(result.get("source")),
            flatten_extensions(result.get("extensions")),
        ]
        if part
    )

    if not person_is_associated(person, association_text):
        return []

    if looks_like_switchboard(association_text):
        return []

    found: list[str] = []
    blobs = collect_result_blobs(result)

    for blob in blobs:
        if looks_like_switchboard(blob):
            continue

        for raw in PHONE_CANDIDATE_RE.findall(blob):
            normalized = normalize_to_e164(raw, person.location)

            if normalized is None:
                continue

            found.append(normalized)

    return list(dict.fromkeys(found))


def person_is_associated(person: NormalizedPerson, text: str) -> bool:
    haystack = text.lower()
    full_name = (person.full_name or "").strip().lower()

    if full_name and len(full_name) >= 5 and full_name in haystack:
        return True

    first = (person.first_name or "").strip().lower()
    last = (person.last_name or "").strip().lower()

    if first and last and len(last) >= 3:
        return first in haystack and last in haystack

    return False


def looks_like_switchboard(text: str) -> bool:
    return bool(SWITCHBOARD_RE.search(text or ""))


def collect_result_blobs(result: dict[str, Any]) -> list[str]:
    blobs: list[str] = []

    for key, value in walk_values(result):
        if not isinstance(value, str) or not value.strip():
            continue

        key_l = (key or "").lower()

        if key_l in PHONE_FIELD_KEYS or "phone" in key_l:
            blobs.append(value)
            continue

        if PHONE_CANDIDATE_RE.search(value):
            blobs.append(value)

    return blobs


def walk_values(obj: Any, key: str | None = None):
    if isinstance(obj, dict):
        for child_key, child in obj.items():
            yield from walk_values(child, str(child_key))
        return

    if isinstance(obj, list):
        for item in obj:
            yield from walk_values(item, key)
        return

    yield key, obj


def flatten_extensions(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        return " ".join(stringify(item) for item in value)

    if isinstance(value, dict):
        return " ".join(stringify(item) for item in value.values())

    return stringify(value)


def stringify(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def normalize_to_e164(raw: str, location: str | None) -> str | None:
    text = (raw or "").strip()

    if not text:
        return None

    plus = text.startswith("+") or text.startswith("00")
    digits = re.sub(r"\D", "", text)

    if text.startswith("00") and len(digits) >= 11:
        digits = digits[2:] if digits.startswith("00") else digits
        plus = True

    if len(digits) < 10 or len(digits) > 15:
        return None

    if TOLL_FREE_RE.match(digits):
        return None

    if plus:
        if len(digits) < 11:
            return None

        return f"+{digits}"

    location_text = location or ""

    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"

    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"

    if len(digits) == 10 and INDIA_LOCATION_RE.search(location_text):
        if digits[0] in "6789":
            return f"+91{digits}"

        return None

    if len(digits) == 10 and US_LOCATION_RE.search(location_text):
        if digits[0] in "23456789":
            return f"+1{digits}"

        return None

    # Do not guess a country code when location is unknown.
    return None
