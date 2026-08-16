from app.config import APOLLO_API_KEY
from app.services.people.base import (
    NormalizedPerson,
    ProviderNotConfiguredError,
    ProviderNotImplementedError,
    SearchCriteria,
)


class ApolloProvider:
    """
    Apollo.io adapter.

    Wire the real people-search HTTP calls here when APOLLO_API_KEY
    is available. Do not invent API responses.
    """

    name = "apollo"

    def search_people(
        self,
        criteria: SearchCriteria,
        limit: int = 10,
    ) -> list[NormalizedPerson]:
        self._require_key()
        raise ProviderNotImplementedError(
            "Apollo search is not wired yet. Add the real Apollo.io "
            "people search request in ApolloProvider.search_people."
        )

    def get_person(self, person_id: str) -> NormalizedPerson | None:
        self._require_key()
        raise ProviderNotImplementedError(
            "Apollo person lookup is not wired yet. Add the real Apollo.io "
            "person request in ApolloProvider.get_person."
        )

    def _require_key(self) -> None:
        if not APOLLO_API_KEY:
            raise ProviderNotConfiguredError(
                "APOLLO_API_KEY is not configured"
            )
