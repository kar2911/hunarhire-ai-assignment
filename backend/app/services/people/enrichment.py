import re
from typing import Any
from urllib.parse import urlparse

from app.services.people.base import (
    EducationItem,
    ExperienceItem,
    NormalizedPerson,
)
from app.services.people.phone import (
    PHONE_SOURCE_PUBLIC_WEB,
    PHONE_SOURCE_RECRUITER,
    discover_public_professional_phone,
)

EMAIL_RE = re.compile(
    r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}",
    re.IGNORECASE,
)

DEGREE_ALIASES = (
    (re.compile(r"\bbachelor of technology\b|\bb\.?\s*tech\b|\bbtech\b", re.I), "B.Tech"),
    (re.compile(r"\bbachelor of engineering\b|\bb\.?\s*e\.?\b", re.I), "B.E."),
    (re.compile(r"\bmaster of technology\b|\bm\.?\s*tech\b|\bmtech\b", re.I), "M.Tech"),
    (re.compile(r"\bmaster of business administration\b|\bmba\b", re.I), "MBA"),
    (re.compile(r"\bbachelor of science\b|\bb\.?\s*sc\.?\b|\bb\.?\s*s\.?\b", re.I), "B.Sc"),
    (re.compile(r"\bmaster of science\b|\bm\.?\s*sc\.?\b|\bm\.?\s*s\.?\b", re.I), "M.S."),
    (re.compile(r"\bbachelor of computer applications\b|\bbca\b", re.I), "BCA"),
    (re.compile(r"\bmaster of computer applications\b|\bmca\b", re.I), "MCA"),
    (re.compile(r"\bph\.?\s*d\.?\b|\bdoctor of philosophy\b", re.I), "Ph.D"),
)

FIELD_AFTER_DEGREE_RE = re.compile(
    r"(?:bachelor of technology|bachelor of engineering|"
    r"bachelor of science|bachelor of computer applications|"
    r"master of technology|master of science|"
    r"master of computer applications|master of business administration|"
    r"b\.?\s*tech|btech|b\.?\s*e\.?|m\.?\s*tech|mtech|mba|"
    r"b\.?\s*sc\.?|m\.?\s*sc\.?|m\.?\s*s\.?|bca|mca|ph\.?\s*d\.?)"
    r"(?:\s*\([^)]+\))?"
    r"\s*(?:,|in)\s+([A-Za-z][A-Za-z0-9&/ \-]{2,80})",
    re.IGNORECASE,
)

SCHOOL_RE = re.compile(
    r"(?:from|at)\s+"
    r"((?:Indian Institute of Technology|IIT|NIT|IIIT|University|College|"
    r"Institute)[^,·\n.]{0,60})",
    re.IGNORECASE,
)

EXPERIENCE_AT_RE = re.compile(
    r"(?:^|[\n·|•.]|\bPreviously\s+|\bFormer\s+)"
    r"\s*"
    r"([A-Z][A-Za-z0-9/+&'’ \-]{2,70}?)"
    r"\s+at\s+"
    r"([A-Z][A-Za-z0-9.&'’ \-]{2,70}?)"
    r"(?=\s*(?:[·|•(,.\n]|$|\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present))",
)

DATE_RANGE_RE = re.compile(
    r"((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\s+\d{4}|\d{4})"
    r"\s*[–—-]\s*"
    r"(Present|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
    r"Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\d{4})",
    re.IGNORECASE,
)

LOCATION_HINT_RE = re.compile(
    r"\b("
    r"bengaluru|bangalore|hyderabad|mumbai|delhi|chennai|pune|gurgaon|"
    r"gurugram|noida|kolkata|ahmedabad|jaipur|kerala|karnataka|telangana|"
    r"maharashtra|india|remote|united states|usa|uk|london|san francisco|"
    r"new york|seattle|austin|california|singapore"
    r")\b",
    re.IGNORECASE,
)

CONNECTIONS_LOCATION_RE = re.compile(
    r"([A-Za-z][A-Za-z .,]{2,60}?)\s*·\s*\d[\d,]*\+?\s+connections",
    re.IGNORECASE,
)

SKILLS_LIST_RE = re.compile(
    r"\bskills?\b\s*[:\-]\s*([^\n.]{3,200})",
    re.IGNORECASE,
)

KNOWN_SKILLS = (
    "machine learning",
    "next.js",
    "node.js",
    "c++",
    "fastapi",
    "postgresql",
    "kubernetes",
    "javascript",
    "typescript",
    "tensorflow",
    "pytorch",
    "graphql",
    "terraform",
    "mongodb",
    "postgres",
    "python",
    "django",
    "flask",
    "react",
    "aws",
    "gcp",
    "azure",
    "docker",
    "linux",
    "redis",
    "java",
    "kotlin",
    "golang",
    "rust",
    "sql",
    "git",
    "nlp",
    "go",
)

NOISE_TITLES = {
    "linkedin",
    "profile",
    "experience",
    "education",
    "skills",
    "about",
    "contact",
}


def linkedin_handle(url: str | None) -> str | None:
    if not url:
        return None

    parsed = urlparse(url)
    match = re.match(r"^/in/([^/]+)/?", parsed.path or "", flags=re.IGNORECASE)

    if not match:
        return None

    handle = match.group(1).strip()

    if not handle or handle.lower() in {"unavailable", "pub", "dir"}:
        return None

    return handle


def build_enrichment_queries(person: NormalizedPerson) -> list[tuple[str, str]]:
    """Return (kind, query) pairs. At most five Google searches."""

    queries: list[tuple[str, str]] = []
    handle = linkedin_handle(person.linkedin_url)

    if handle:
        site = f"site:linkedin.com/in/{handle}"
        title = (person.job_title or "Senior Software Engineer").strip()
        queries.append(("profile", site))
        queries.append(("experience", f'{site} (experience OR "{title}")'))
        queries.append(
            (
                "education",
                f'{site} (education OR "B.Tech" OR "Computer Science")',
            )
        )
        queries.append(("skills", f"{site} Python FastAPI skills"))

    name = (person.full_name or "").strip()

    if name:
        contact_parts = [f'"{name}"']

        if person.company_name:
            contact_parts.append(f'"{person.company_name.strip()}"')

        contact_parts.append("(phone OR mobile OR contact)")
        queries.append(("contact", " ".join(contact_parts)))

    return queries[:5]


def extract_fields_from_payload(
    payload: dict[str, Any],
    person: NormalizedPerson | None = None,
) -> dict[str, Any]:
    blobs = collect_serp_blobs(payload)
    combined = " \n ".join(blobs)

    return {
        "location": extract_location(combined),
        "skills": extract_skills(combined),
        "experience": extract_experience(combined),
        "education": extract_education(combined),
        "headline": extract_headline(payload),
        "summary": extract_summary(blobs),
        "email": extract_email_from_text(combined, person),
        "job_title": None,
        "company_name": None,
        "full_name": None,
    }


def collect_serp_blobs(payload: dict[str, Any]) -> list[str]:
    blobs: list[str] = []

    for result in iter_results(payload):
        blobs.extend(blobs_from_result(result))

    for key in ("knowledge_graph", "answer_box"):
        block = payload.get(key)

        if isinstance(block, dict):
            blobs.extend(blobs_from_result(block))

    return [blob for blob in blobs if blob]


def iter_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    organic = payload.get("organic_results") or []

    if not isinstance(organic, list):
        return []

    return [item for item in organic if isinstance(item, dict)]


def blobs_from_result(result: dict[str, Any]) -> list[str]:
    blobs: list[str] = []

    for key in ("title", "snippet", "source"):
        value = result.get(key)

        if isinstance(value, str) and value.strip():
            blobs.append(value.strip())

    extensions = result.get("extensions")

    if isinstance(extensions, list):
        blobs.extend(str(item) for item in extensions if item)
    elif isinstance(extensions, str) and extensions.strip():
        blobs.append(extensions.strip())

    for key in ("rich_snippet", "rich_snippet_table"):
        blobs.extend(flatten_strings(result.get(key)))

    sitelinks = result.get("sitelinks")

    if isinstance(sitelinks, dict):
        for group in sitelinks.values():
            if isinstance(group, list):
                for link in group:
                    if isinstance(link, dict):
                        blobs.extend(blobs_from_result(link))
                    elif isinstance(link, str):
                        blobs.append(link)
    elif isinstance(sitelinks, list):
        for link in sitelinks:
            if isinstance(link, dict):
                blobs.extend(blobs_from_result(link))

    highlighted = result.get("snippet_highlighted_words")

    if isinstance(highlighted, list):
        blobs.extend(str(item) for item in highlighted if item)

    return blobs


def flatten_strings(value: Any) -> list[str]:
    found: list[str] = []

    if isinstance(value, str):
        text = value.strip()

        if text:
            found.append(text)
        return found

    if isinstance(value, dict):
        for child in value.values():
            found.extend(flatten_strings(child))
        return found

    if isinstance(value, list):
        for child in value:
            found.extend(flatten_strings(child))

    return found


def extract_location(text: str) -> str | None:
    connections = CONNECTIONS_LOCATION_RE.search(text)

    if connections:
        candidate = clean_location(connections.group(1))

        if candidate:
            return candidate

    for line in re.split(r"[\n·|]", text):
        candidate = clean_location(line)

        if candidate:
            return candidate

    return None


def clean_location(value: str) -> str | None:
    text = re.sub(r"\s+", " ", (value or "").strip(" .,-"))

    if not text or len(text) < 3 or len(text) > 80:
        return None

    hint = LOCATION_HINT_RE.search(text)

    if not hint:
        return None

    if "@" in text or "http" in text.lower():
        return None

    if re.search(
        r"\b(developer|engineer|manager|python|fastapi|skills?|experience)\b",
        text,
        flags=re.IGNORECASE,
    ):
        start = max(0, hint.start() - 24)
        end = min(len(text), hint.end() + 24)
        fragment = text[start:end]
        fragment = re.sub(r"^[^A-Za-z]+", "", fragment)
        fragment = re.sub(
            r"\b(developer|engineer|manager|python|fastapi|senior).*$",
            "",
            fragment,
            flags=re.IGNORECASE,
        )
        fragment = fragment.strip(" .,-·|")
        return fragment if fragment and LOCATION_HINT_RE.search(fragment) else hint.group(1).title()

    return text


def extract_skills(text: str) -> list[str]:
    found: list[str] = []

    for labeled in SKILLS_LIST_RE.finditer(text or ""):
        chunk = labeled.group(1)

        for part in re.split(r"[,;/]| and ", chunk):
            skill = normalize_skill_label(part)

            if skill and skill not in found:
                found.append(skill)

        lower = chunk.lower()

        for skill in KNOWN_SKILLS:
            pattern = r"(?<![A-Za-z])" + re.escape(skill) + r"(?![A-Za-z])"

            if skill == "go" and not re.search(r"\bgo\b", lower):
                continue

            if re.search(pattern, lower) and display_skill(skill) not in found:
                found.append(display_skill(skill))

    for part in re.split(r"[|,]", text or ""):
        lowered = part.strip().lower()

        if lowered in {skill.lower() for skill in KNOWN_SKILLS}:
            label = display_skill(lowered)

            if label not in found:
                found.append(label)

    return found[:12]


def normalize_skill_label(value: str) -> str | None:
    text = re.sub(r"\s+", " ", (value or "").strip(" ."))

    if not text or len(text) < 2 or len(text) > 40:
        return None

    if LOCATION_HINT_RE.search(text) or text.lower() in NOISE_TITLES:
        return None

    return display_skill(text)


def display_skill(value: str) -> str:
    lowered = value.strip()
    specials = {
        "c++": "C++",
        "next.js": "Next.js",
        "node.js": "Node.js",
        "fastapi": "FastAPI",
        "postgresql": "PostgreSQL",
        "graphql": "GraphQL",
        "aws": "AWS",
        "gcp": "GCP",
        "sql": "SQL",
        "nlp": "NLP",
    }

    if lowered.lower() in specials:
        return specials[lowered.lower()]

    if lowered.lower() in {"python", "django", "flask", "react", "docker"}:
        return lowered.capitalize()

    return lowered


def extract_experience(text: str) -> list[ExperienceItem]:
    items: list[ExperienceItem] = []
    seen: set[tuple[str, str]] = set()

    for match in EXPERIENCE_AT_RE.finditer(text):
        title = clean_role(match.group(1))
        company = clean_company(match.group(2))

        if not title or not company:
            continue

        key = (title.lower(), company.lower())

        if key in seen:
            continue

        seen.add(key)
        window = text[max(0, match.start() - 20) : match.end() + 48]
        start, end = extract_dates(window)
        location = extract_location(window)
        items.append(
            ExperienceItem(
                title=title,
                company=company,
                location=location,
                start_date=start,
                end_date=end,
            )
        )

    return items[:8]


def extract_dates(text: str) -> tuple[str | None, str | None]:
    match = DATE_RANGE_RE.search(text or "")

    if not match:
        return None, None

    start = re.sub(r"\s+", " ", match.group(1)).strip()
    end = re.sub(r"\s+", " ", match.group(2)).strip()

    if end.lower() == "present":
        end = "Present"

    return start, end


def clean_role(value: str) -> str | None:
    text = re.sub(r"\s+", " ", (value or "").strip(" ·-|"))
    text = re.sub(
        r"^(?:Previously|Former|Currently|Current)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    if not text or text.lower() in NOISE_TITLES or len(text) > 80:
        return None

    if LOCATION_HINT_RE.fullmatch(text):
        return None

    return text


def clean_company(value: str) -> str | None:
    text = re.sub(r"\s+", " ", (value or "").strip(" ·-|"))
    text = re.sub(r"\s+\d{4}$", "", text).strip()

    if not text or text.lower() in NOISE_TITLES or len(text) > 80:
        return None

    return text


def extract_education(text: str) -> list[EducationItem]:
    items: list[EducationItem] = []
    seen: set[tuple[str | None, str | None, str | None]] = set()

    for pattern, canonical in DEGREE_ALIASES:
        for match in pattern.finditer(text):
            window = text[match.start() : min(len(text), match.end() + 90)]
            nearby = text[max(0, match.start() - 80) : match.end() + 90]
            field = extract_field(window)
            school = extract_school(nearby)
            start, end = extract_dates(nearby)
            key = (canonical, field, school)

            if key in seen:
                continue

            seen.add(key)
            items.append(
                EducationItem(
                    school=school,
                    degree=canonical,
                    field=field,
                    start_date=start,
                    end_date=end,
                )
            )

    return items[:6]


def extract_field(window: str) -> str | None:
    match = FIELD_AFTER_DEGREE_RE.search(window)

    if not match:
        return None

    field = re.sub(r"\s+", " ", match.group(1)).strip(" .,")
    field = re.sub(r"\s+\d{4}.*$", "", field).strip()

    if not field or len(field) < 3:
        return None

    lowered = field.lower()

    if "computer science and engineering" in lowered:
        return "Computer Science and Engineering"

    if "computer science" in lowered:
        if "engineering" in lowered:
            return "Computer Science and Engineering"

        return "Computer Science"

    return field


def extract_school(window: str) -> str | None:
    match = SCHOOL_RE.search(window or "")

    if not match:
        return None

    school = re.sub(r"\s+", " ", match.group(1)).strip(" .,")
    return school or None


def extract_headline(payload: dict[str, Any]) -> str | None:
    for result in iter_results(payload):
        title = (result.get("title") or "").strip()
        cleaned = re.sub(
            r"\s*[\-|]\s*LinkedIn\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()

        if cleaned and cleaned.lower() not in NOISE_TITLES:
            return cleaned

        snippet = (result.get("snippet") or "").strip()

        if snippet:
            return snippet.split("·")[0].strip() or None

    return None


def extract_summary(blobs: list[str]) -> str | None:
    snippets = [blob for blob in blobs if len(blob) > 40]

    if not snippets:
        return None

    unique: list[str] = []

    for blob in snippets:
        if blob not in unique:
            unique.append(blob)

    return " ".join(unique[:3]) if unique else None


def extract_email_from_text(text: str, person: NormalizedPerson | None = None) -> str | None:
    match = EMAIL_RE.search(text or "")

    if not match:
        return None

    email = match.group(0)
    local = email.split("@", 1)[0].lower()

    if person:
        last = (person.last_name or "").lower().replace(" ", "")
        first = (person.first_name or "").lower().replace(" ", "")

        if last and last not in local and not (first and first in local):
            return None

    return email


def apply_extracted_fields(
    person: NormalizedPerson,
    extracted: dict[str, Any],
    *,
    phone: str | None = None,
) -> NormalizedPerson:
    updates: dict[str, Any] = {}

    for field in (
        "full_name",
        "job_title",
        "company_name",
        "location",
        "headline",
        "summary",
        "email",
    ):
        current = getattr(person, field)
        incoming = extracted.get(field)

        if not current and incoming:
            updates[field] = incoming

    incoming_skills = extracted.get("skills") or []
    skills = list(person.skills)

    for skill in incoming_skills:
        if skill not in skills:
            skills.append(skill)

    if skills != person.skills:
        updates["skills"] = skills

    experience = merge_experience(
        person.experience,
        extracted.get("experience") or [],
    )

    if experience != person.experience:
        updates["experience"] = experience

    education = merge_education(
        person.education,
        extracted.get("education") or [],
    )

    if education != person.education:
        updates["education"] = education

    if phone:
        updates["public_phone"] = phone

        if person.phone_source != PHONE_SOURCE_RECRUITER:
            updates["phone"] = phone
            updates["phone_source"] = PHONE_SOURCE_PUBLIC_WEB

    if not updates:
        return person

    return person.model_copy(update=updates)


def merge_experience(
    existing: list[ExperienceItem],
    incoming: list[ExperienceItem],
) -> list[ExperienceItem]:
    merged = list(existing)
    seen_keys = {
        ((item.title or "").lower(), (item.company or "").lower())
        for item in existing
    }

    for item in incoming:
        key = ((item.title or "").lower(), (item.company or "").lower())

        if not item.title and not item.company:
            continue

        if key in seen_keys:
            continue

        seen_keys.add(key)
        merged.append(item)

    return merged[:8]


def merge_education(
    existing: list[EducationItem],
    incoming: list[EducationItem],
) -> list[EducationItem]:
    merged = list(existing)
    seen = {
        (
            (item.degree or "").lower(),
            (item.field or "").lower(),
            (item.school or "").lower(),
        )
        for item in existing
    }

    for item in incoming:
        key = (
            (item.degree or "").lower(),
            (item.field or "").lower(),
            (item.school or "").lower(),
        )

        if key in seen:
            continue

        if not item.degree and not item.field and not item.school:
            continue

        seen.add(key)
        merged.append(item)

    return merged[:6]


def enrich_person_from_payloads(
    person: NormalizedPerson,
    payloads: list[tuple[str, dict[str, Any]]],
) -> NormalizedPerson:
    updated = person
    contact_payloads: list[dict[str, Any]] = []

    for kind, payload in payloads:
        if not isinstance(payload, dict):
            continue

        extracted = extract_fields_from_payload(payload, person=updated)

        if kind in {"profile", "experience"}:
            title, company = title_company_from_payload(payload)

            if title:
                extracted["job_title"] = extracted.get("job_title") or title

            if company:
                extracted["company_name"] = extracted.get("company_name") or company

        if kind == "contact":
            contact_payloads.append(payload)
            extracted["skills"] = []
            extracted["experience"] = []
            extracted["education"] = []

        if kind == "skills":
            extracted["experience"] = []
            extracted["education"] = []

        if kind == "education":
            extracted["experience"] = []

        if kind == "experience":
            extracted["education"] = []

        updated = apply_extracted_fields(updated, extracted)

    phone = None

    for payload in contact_payloads:
        phone = discover_public_professional_phone(updated, payload)

        if phone:
            break

    if phone:
        updated = apply_extracted_fields(updated, {}, phone=phone)

    return updated


def title_company_from_payload(
    payload: dict[str, Any],
) -> tuple[str | None, str | None]:
    for result in iter_results(payload):
        title = (result.get("title") or "").strip()

        if not title:
            continue

        cleaned = re.sub(
            r"\s*[\-|]\s*LinkedIn\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()
        parts = [
            part.strip()
            for part in re.split(r"\s+[-–—]\s+", cleaned)
            if part.strip()
        ]
        job_title = parts[1] if len(parts) > 1 else None
        company_name = parts[2] if len(parts) > 2 else None

        if job_title and "|" in job_title:
            segments = [part.strip() for part in job_title.split("|") if part.strip()]
            job_title = segments[0] if segments else job_title

        if job_title and " at " in job_title and not company_name:
            job_title, company_name = job_title.split(" at ", 1)
            job_title = job_title.strip() or None
            company_name = company_name.strip() or None

        if job_title or company_name:
            return job_title, company_name

    return None, None
