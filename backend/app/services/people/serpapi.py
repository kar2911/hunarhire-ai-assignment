import hashlib
import re
from typing import Any
from urllib.parse import urlparse

import requests

from app.config import SERPAPI_API_KEY
from app.services.people.base import (
    NormalizedPerson,
    ProviderNotConfiguredError,
    ProviderRequestError,
    SearchCriteria,
)
from app.services.people.mapper import to_normalized_person
from app.services.people.phone import PHONE_SOURCE_RECRUITER
from app.services.people.enrichment import (
    apply_extracted_fields,
    build_enrichment_queries,
    enrich_person_from_payloads,
    extract_fields_from_payload,
)

SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
LINKEDIN_PROFILE_HOST = "linkedin.com"
EMAIL_RE = re.compile(
    r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}",
    re.IGNORECASE,
)


class SerpApiProvider:
    """
    Public-profile discovery via SerpApi Google Search.

    This is not a people database. Results are public web search hits,
    typically LinkedIn profile pages returned by Google.
    """

    name = "serpapi"

    def search_people(
        self,
        criteria: SearchCriteria,
        limit: int = 10,
    ) -> list[NormalizedPerson]:
        api_key = (SERPAPI_API_KEY or "").strip()

        if not api_key:
            raise ProviderNotConfiguredError(
                "People search provider is not configured."
            )

        query = build_google_query(criteria)
        count = min(max(limit, 1), 10)
        payload = google_search(query, count, api_key)
        organic_results = payload.get("organic_results") or []

        if not isinstance(organic_results, list):
            return []

        people: list[NormalizedPerson] = []
        seen_urls: set[str] = set()

        for result in organic_results:
            if len(people) >= count:
                break

            if not isinstance(result, dict):
                continue

            person = self._normalize_result(result)

            if person is None or not person.linkedin_url:
                continue

            if person.linkedin_url in seen_urls:
                continue

            seen_urls.add(person.linkedin_url)
            people.append(person)

        return people

    def get_person(self, person_id: str) -> NormalizedPerson | None:
        return None

    def enrich_person(self, person: NormalizedPerson) -> NormalizedPerson:
        """
        Up to five public Google searches for a selected profile.

        Results are cached by the people route so this runs once per person.
        Does not scrape LinkedIn and does not invent values.
        """

        queries = build_enrichment_queries(person)

        if person.phone_source == PHONE_SOURCE_RECRUITER:
            queries = [item for item in queries if item[0] != "contact"]

        if not queries:
            return person

        api_key = (SERPAPI_API_KEY or "").strip()

        if not api_key:
            raise ProviderNotConfiguredError(
                "People search provider is not configured."
            )

        payloads: list[tuple[str, dict]] = []

        for kind, query in queries:
            payloads.append((kind, google_search(query, 5, api_key)))

        return enrich_person_from_payloads(person, payloads)

    def _normalize_result(
        self,
        result: dict[str, Any],
    ) -> NormalizedPerson | None:
        linkedin_url = extract_linkedin_profile_url(
            result.get("link") or result.get("redirect_link")
        )

        if not linkedin_url:
            return None

        title = (result.get("title") or "").strip()
        snippet = (result.get("snippet") or "").strip() or None
        full_name, job_title, company_name = parse_linkedin_serp_title(title)
        email = extract_email(snippet)

        provider_id = hashlib.sha256(
            linkedin_url.encode("utf-8")
        ).hexdigest()[:16]

        first_name = None
        last_name = None

        if full_name:
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else None
            last_name = (
                " ".join(name_parts[1:]) if len(name_parts) > 1 else None
            )

        person = to_normalized_person(
            provider=self.name,
            provider_id=provider_id,
            raw={
                "full_name": full_name,
                "first_name": first_name,
                "last_name": last_name,
                "job_title": job_title,
                "company_name": company_name,
                "location": None,
                "linkedin_url": linkedin_url,
                "headline": snippet,
                "summary": snippet,
                "skills": [],
                "email": email,
                "phone": None,
                "experience": [],
                "education": [],
            },
        )

        extracted = extract_fields_from_payload(
            {"organic_results": [result]},
            person=person,
        )

        if job_title:
            extracted["job_title"] = None

        if company_name:
            extracted["company_name"] = None

        if snippet:
            extracted["headline"] = None
            extracted["summary"] = None

        return apply_extracted_fields(person, extracted)


def build_google_query(criteria: SearchCriteria) -> str:
    parts = ["site:linkedin.com/in"]

    if criteria.job_title:
        parts.append(f'"{criteria.job_title.strip()}"')
    elif criteria.seniority:
        parts.append(f'"{criteria.seniority.strip()}"')

    for skill in criteria.skills[:3]:
        cleaned = skill.strip()

        if cleaned:
            parts.append(f'"{cleaned}"')

    if criteria.location:
        parts.append(f'"{criteria.location.strip()}"')

    return " ".join(parts)


def parse_linkedin_serp_title(
    title: str,
) -> tuple[str | None, str | None, str | None]:
    cleaned = re.sub(
        r"\s*[\-|]\s*LinkedIn\s*$",
        "",
        title.strip(),
        flags=re.IGNORECASE,
    ).strip()

    if not cleaned:
        return None, None, None

    parts = [part.strip() for part in re.split(r"\s+[-–—]\s+", cleaned) if part.strip()]
    full_name = parts[0] if parts else None
    job_title = parts[1] if len(parts) > 1 else None
    company_name = parts[2] if len(parts) > 2 else None

    if job_title and "|" in job_title:
        segments = [part.strip() for part in job_title.split("|") if part.strip()]
        job_title = segments[0] if segments else job_title

    if job_title and " at " in job_title and not company_name:
        job_title, company_name = job_title.split(" at ", 1)
        job_title = job_title.strip() or None
        company_name = company_name.strip() or None

    return full_name, job_title, company_name


def extract_linkedin_profile_url(value: Any) -> str | None:
    if not value or not isinstance(value, str):
        return None

    parsed = urlparse(value.strip())

    if parsed.scheme not in {"http", "https"}:
        return None

    host = (parsed.netloc or "").lower()

    if host.startswith("www."):
        host = host[4:]

    if not host.endswith(LINKEDIN_PROFILE_HOST):
        return None

    path = parsed.path or ""
    match = re.match(r"^/in/([^/]+)/?", path, flags=re.IGNORECASE)

    if not match:
        return None

    slug = match.group(1)

    if slug.lower() in {"unavailable", "pub", "dir"}:
        return None

    return f"https://www.linkedin.com/in/{slug}"


def extract_email(text: str | None) -> str | None:
    if not text:
        return None

    match = EMAIL_RE.search(text)

    if not match:
        return None

    return match.group(0)


def build_phone_discovery_query(person: NormalizedPerson) -> str | None:
    name = (person.full_name or "").strip()

    if not name:
        first = (person.first_name or "").strip()
        last = (person.last_name or "").strip()
        name = " ".join(part for part in [first, last] if part).strip()

    if not name:
        return None

    parts = [f'"{name}"']

    if person.company_name:
        parts.append(f'"{person.company_name.strip()}"')

    if person.job_title:
        parts.append(f'"{person.job_title.strip()}"')

    parts.append(
        '(phone OR contact OR office OR "work phone" OR "business phone")'
    )

    return " ".join(parts)


def google_search(query: str, num: int, api_key: str) -> dict[str, Any]:
    try:
        response = requests.get(
            SERPAPI_SEARCH_URL,
            params={
                "engine": "google",
                "q": query,
                "num": num,
                "api_key": api_key,
            },
            timeout=30,
        )
    except requests.RequestException:
        raise ProviderRequestError(
            "People search is temporarily unavailable.",
            status_code=502,
        ) from None

    if response.status_code in {401, 403}:
        raise ProviderRequestError(
            "People search provider authentication failed.",
            status_code=401,
        )

    if response.status_code == 429:
        raise ProviderRequestError(
            "People search is rate limited. Try again shortly.",
            status_code=429,
        )

    if response.status_code >= 400:
        raise ProviderRequestError(
            "People search is temporarily unavailable.",
            status_code=502,
        )

    try:
        payload = response.json()
    except ValueError:
        raise ProviderRequestError(
            "People search returned an unexpected response.",
            status_code=502,
        ) from None

    if not isinstance(payload, dict):
        raise ProviderRequestError(
            "People search returned an unexpected response.",
            status_code=502,
        )

    if payload.get("error"):
        message = str(payload.get("error") or "")

        if "hasn't returned any results" in message.lower():
            return {"organic_results": []}

        raise ProviderRequestError(
            "People search is temporarily unavailable.",
            status_code=502,
        )

    return payload
