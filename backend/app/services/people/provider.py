from app.config import PEOPLE_PROVIDER
from app.services.people.apollo import ApolloProvider
from app.services.people.base import PeopleProvider
from app.services.people.coresignal import CoresignalProvider
from app.services.people.demo import DemoPeopleProvider
from app.services.people.mock import MockPeopleProvider
from app.services.people.pdl import PDLProvider
from app.services.people.serpapi import SerpApiProvider

PROVIDERS = {
    "mock": MockPeopleProvider,
    "demo": DemoPeopleProvider,
    "serpapi": SerpApiProvider,
    "pdl": PDLProvider,
    "apollo": ApolloProvider,
    "coresignal": CoresignalProvider,
}


def get_people_provider() -> PeopleProvider:
    provider_name = (PEOPLE_PROVIDER or "mock").strip().lower()
    provider_cls = PROVIDERS.get(provider_name)

    if provider_cls is None:
        raise ValueError(
            f"Unsupported PEOPLE_PROVIDER '{provider_name}'. "
            "Use mock, demo, serpapi, pdl, apollo, or coresignal."
        )

    return provider_cls()
