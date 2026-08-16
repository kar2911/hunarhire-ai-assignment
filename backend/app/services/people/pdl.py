from app.config import PDL_API_KEY
from app.services.people.base import (
    NormalizedPerson,
    ProviderNotConfiguredError,
    ProviderNotImplementedError,
    SearchCriteria,
)


class PDLProvider:
    """
    People Data Labs adapter.

    Wire the real Person Search / Person Enrichment HTTP calls here
    when PDL_API_KEY is available. Do not invent API responses.
    """

    name = "pdl"

    def search_people(
        self,
        criteria: SearchCriteria,
        limit: int = 10,
    ) -> list[NormalizedPerson]:
        self._require_key()
        raise ProviderNotImplementedError(
            "PDL search is not wired yet. Add the real People Data Labs "
            "Person Search request in PDLProvider.search_people."
        )

    def get_person(self, person_id: str) -> NormalizedPerson | None:
        self._require_key()
        raise ProviderNotImplementedError(
            "PDL person lookup is not wired yet. Add the real People Data "
            "Labs Person Enrichment request in PDLProvider.get_person."
        )

    def _require_key(self) -> None:
        if not PDL_API_KEY:
            raise ProviderNotConfiguredError(
                "PDL_API_KEY is not configured"
            )
