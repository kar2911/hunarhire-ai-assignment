from app.config import CORESIGNAL_API_KEY
from app.services.people.base import (
    NormalizedPerson,
    ProviderNotConfiguredError,
    ProviderNotImplementedError,
    SearchCriteria,
)


class CoresignalProvider:
    """
    Coresignal adapter.

    Wire the real employee-search HTTP calls here when
    CORESIGNAL_API_KEY is available. Do not invent API responses.
    """

    name = "coresignal"

    def search_people(
        self,
        criteria: SearchCriteria,
        limit: int = 10,
    ) -> list[NormalizedPerson]:
        self._require_key()
        raise ProviderNotImplementedError(
            "Coresignal search is not wired yet. Add the real Coresignal "
            "request in CoresignalProvider.search_people."
        )

    def get_person(self, person_id: str) -> NormalizedPerson | None:
        self._require_key()
        raise ProviderNotImplementedError(
            "Coresignal person lookup is not wired yet. Add the real "
            "Coresignal request in CoresignalProvider.get_person."
        )

    def _require_key(self) -> None:
        if not CORESIGNAL_API_KEY:
            raise ProviderNotConfiguredError(
                "CORESIGNAL_API_KEY is not configured"
            )
