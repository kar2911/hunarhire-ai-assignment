import re
from typing import Protocol

from app.services.people.base import SearchCriteria

KNOWN_SKILLS = (
    "python",
    "fastapi",
    "django",
    "flask",
    "postgresql",
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "aws",
    "gcp",
    "azure",
    "react",
    "next.js",
    "nextjs",
    "typescript",
    "javascript",
    "node.js",
    "nodejs",
    "java",
    "kotlin",
    "go",
    "golang",
    "rust",
    "c++",
    "sql",
    "graphql",
    "docker",
    "kubernetes",
    "terraform",
    "linux",
    "git",
    "machine learning",
    "ml",
    "nlp",
    "pytorch",
    "tensorflow",
)

SENIORITY_PATTERNS = (
    ("principal", "principal"),
    ("staff", "staff"),
    ("lead", "lead"),
    ("senior", "senior"),
    ("mid-level", "mid"),
    ("mid level", "mid"),
    ("junior", "junior"),
    ("intern", "intern"),
    ("director", "director"),
    ("head of", "head"),
)

LOOKING_FOR_RE = re.compile(
    r"(?:looking for|hiring|seeking|need)\s+(?:a |an |the )?"
    r"([^.,\n]+?)(?:\s+with\b|\s+who\b|,|\.|$)",
    re.IGNORECASE,
)

YEARS_RE = re.compile(
    r"(\d+)\s*\+?\s*(?:years|yrs)\b",
    re.IGNORECASE,
)

LOCATION_RE = re.compile(
    r"(?:based in|located in|in)\s+"
    r"([A-Za-z][A-Za-z .]+?)"
    r"(?:\s+or\b|,|\.|$)",
    re.IGNORECASE,
)

COMPANY_RE = re.compile(
    r"(?:at|for)\s+([A-Z][A-Za-z0-9.& ]{1,40})",
)


class JobCriteriaExtractor(Protocol):
    def extract(self, job_description: str) -> SearchCriteria:
        ...


class HeuristicJobCriteriaExtractor:
    """
    Deterministic fallback extractor.

    Replace this class with an LLM-backed extractor later without
    changing the search API or people-provider contracts.
    """

    def extract(self, job_description: str) -> SearchCriteria:
        text = job_description.strip()
        lowered = text.lower()

        job_title = self._extract_job_title(text)
        skills = self._extract_skills(lowered)
        location = self._extract_location(text)
        seniority = self._extract_seniority(lowered, job_title)
        years_experience = self._extract_years(text)
        company = self._extract_company(text, job_title)
        keywords = self._extract_keywords(lowered)

        return SearchCriteria(
            job_title=job_title,
            skills=skills,
            location=location,
            seniority=seniority,
            years_experience=years_experience,
            company=company,
            keywords=keywords,
        )

    def _extract_job_title(self, text: str) -> str | None:
        match = LOOKING_FOR_RE.search(text)

        if match:
            title = match.group(1).strip(" .,-")
            title = re.sub(
                r"\s+with\s+\d+.*$",
                "",
                title,
                flags=re.IGNORECASE,
            )
            return title or None

        first_line = text.split("\n", 1)[0].strip()

        if 3 <= len(first_line) <= 80:
            return first_line

        return None

    def _extract_skills(self, lowered: str) -> list[str]:
        found: list[str] = []
        labels = {
            "postgres": "PostgreSQL",
            "postgresql": "PostgreSQL",
            "fastapi": "FastAPI",
            "nextjs": "Next.js",
            "next.js": "Next.js",
            "nodejs": "Node.js",
            "node.js": "Node.js",
            "golang": "Go",
            "ml": "ML",
            "nlp": "NLP",
            "aws": "AWS",
            "gcp": "GCP",
            "c++": "C++",
            "sql": "SQL",
        }

        for skill in KNOWN_SKILLS:
            if not self._contains_skill(lowered, skill):
                continue

            label = labels.get(skill, skill.title())

            if label not in found:
                found.append(label)

        return found

    def _contains_skill(self, lowered: str, skill: str) -> bool:
        escaped = re.escape(skill)
        pattern = rf"(?<![a-z0-9+]){escaped}(?![a-z0-9+])"
        return re.search(pattern, lowered) is not None

    def _extract_location(self, text: str) -> str | None:
        match = LOCATION_RE.search(text)

        if not match:
            return None

        location = match.group(1).strip(" .,-")
        location = re.sub(
            r"\s+or willing to relocate.*$",
            "",
            location,
            flags=re.IGNORECASE,
        )

        if location.lower() in {"the", "a", "an"}:
            return None

        return location or None

    def _extract_seniority(
        self,
        lowered: str,
        job_title: str | None,
    ) -> str | None:
        haystack = f"{job_title or ''} {lowered}".lower()

        for needle, value in SENIORITY_PATTERNS:
            if needle in haystack:
                return value

        return None

    def _extract_years(self, text: str) -> int | None:
        match = YEARS_RE.search(text)

        if not match:
            return None

        return int(match.group(1))

    def _extract_company(
        self,
        text: str,
        job_title: str | None,
    ) -> str | None:
        if job_title and " at " in job_title.lower():
            return job_title.split(" at ", 1)[-1].strip() or None

        match = COMPANY_RE.search(text)

        if not match:
            return None

        company = match.group(1).strip()

        if company.lower() in {"a", "an", "the", "our"}:
            return None

        return company

    def _extract_keywords(self, lowered: str) -> list[str]:
        keywords: list[str] = []

        for word in (
            "backend",
            "frontend",
            "fullstack",
            "full-stack",
            "remote",
            "relocate",
            "hybrid",
            "on-site",
            "onsite",
        ):
            if word in lowered:
                keywords.append(word)

        return keywords


def get_job_criteria_extractor() -> JobCriteriaExtractor:
    """
    Swap this return value for an LLM extractor later.
    """

    return HeuristicJobCriteriaExtractor()


def extract_search_criteria(job_description: str) -> SearchCriteria:
    return get_job_criteria_extractor().extract(job_description)
