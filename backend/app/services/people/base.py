from typing import Protocol

from pydantic import BaseModel, Field


class SearchCriteria(BaseModel):
    job_title: str | None = None
    skills: list[str] = Field(default_factory=list)
    location: str | None = None
    seniority: str | None = None
    years_experience: int | None = None
    company: str | None = None
    keywords: list[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class EducationItem(BaseModel):
    school: str | None = None
    degree: str | None = None
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class NormalizedPerson(BaseModel):
    id: str
    provider: str
    provider_id: str
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    job_title: str | None = None
    company_name: str | None = None
    company_website: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    skills: list[str] = Field(default_factory=list)
    headline: str | None = None
    summary: str | None = None
    email: str | None = None
    phone: str | None = None
    phone_source: str | None = None
    public_phone: str | None = None
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)


class PeopleProvider(Protocol):
    name: str

    def search_people(
        self,
        criteria: SearchCriteria,
        limit: int = 10,
    ) -> list[NormalizedPerson]:
        ...

    def get_person(self, person_id: str) -> NormalizedPerson | None:
        ...


class ProviderNotConfiguredError(Exception):
    pass


class ProviderNotImplementedError(Exception):
    pass


class ProviderRequestError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code
