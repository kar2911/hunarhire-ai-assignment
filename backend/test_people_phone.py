import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.people.base import NormalizedPerson
from app.services.people.cache import clear_people_cache, store_people
from app.services.people.phone import (
    PHONE_SOURCE_PUBLIC_WEB,
    PHONE_SOURCE_RECRUITER,
    discover_public_professional_phone,
    normalize_to_e164,
)
from app.services.people.serpapi import (
    SerpApiProvider,
    build_phone_discovery_query,
)


client = TestClient(app)


def person(**overrides) -> NormalizedPerson:
    data = {
        "id": "serpapi:test-person",
        "provider": "serpapi",
        "provider_id": "test-person",
        "full_name": "Anita Sharma",
        "first_name": "Anita",
        "last_name": "Sharma",
        "job_title": "Engineering Manager",
        "company_name": "Example Labs",
        "location": "Bengaluru, India",
        "phone": None,
        "phone_source": None,
        "public_phone": None,
    }
    data.update(overrides)
    return NormalizedPerson(**data)


ASSOCIATED_RESULT = {
    "title": "Anita Sharma — Engineering Manager at Example Labs",
    "snippet": (
        "Office contact for Anita Sharma, Engineering Manager. "
        "Work phone +91 98765 43210."
    ),
    "rich_snippet": {
        "top": {
            "detected_extensions": {
                "phone": "+91 98765 43210",
            }
        }
    },
}


class PhoneNormalizationTests(unittest.TestCase):
    def test_e164_from_plus_number(self):
        self.assertEqual(
            normalize_to_e164("+91 98765 43210", "Bengaluru, India"),
            "+919876543210",
        )

    def test_india_location_adds_country_code(self):
        self.assertEqual(
            normalize_to_e164("9876543210", "Bengaluru, India"),
            "+919876543210",
        )

    def test_does_not_guess_country_without_location(self):
        self.assertIsNone(normalize_to_e164("9876543210", None))

    def test_rejects_short_or_incomplete_numbers(self):
        self.assertIsNone(normalize_to_e164("+91 98765", "India"))

    def test_rejects_toll_free(self):
        self.assertIsNone(normalize_to_e164("1800 123 4567", "India"))


class PhoneDiscoveryTests(unittest.TestCase):
    def test_extracts_associated_professional_number(self):
        payload = {"organic_results": [ASSOCIATED_RESULT]}
        self.assertEqual(
            discover_public_professional_phone(person(), payload),
            "+919876543210",
        )

    def test_reads_rich_snippet_phone_field(self):
        payload = {
            "organic_results": [
                {
                    "title": "Anita Sharma profile",
                    "snippet": "Engineering Manager at Example Labs.",
                    "rich_snippet": {
                        "bottom": {
                            "detected_extensions": {
                                "phone": "+91 98765 43210",
                            }
                        }
                    },
                }
            ]
        }
        self.assertEqual(
            discover_public_professional_phone(person(), payload),
            "+919876543210",
        )

    def test_missing_number_returns_none(self):
        payload = {
            "organic_results": [
                {
                    "title": "Anita Sharma — Engineering Manager",
                    "snippet": "Public LinkedIn profile. No contact number listed.",
                }
            ]
        }
        self.assertIsNone(
            discover_public_professional_phone(person(), payload)
        )

    def test_ambiguous_numbers_are_ignored(self):
        payload = {
            "organic_results": [
                {
                    "title": "Anita Sharma Example Labs",
                    "snippet": "Call Anita Sharma at +91 98765 43210.",
                },
                {
                    "title": "Anita Sharma speaking",
                    "snippet": "Contact Anita Sharma on +91 91234 56789.",
                },
            ]
        }
        self.assertIsNone(
            discover_public_professional_phone(person(), payload)
        )

    def test_unrelated_person_number_is_ignored(self):
        payload = {
            "organic_results": [
                {
                    "title": "Ravi Kumar — Director",
                    "snippet": "Call Ravi Kumar at +91 98765 43210.",
                }
            ]
        }
        self.assertIsNone(
            discover_public_professional_phone(person(), payload)
        )

    def test_company_switchboard_is_not_assigned(self):
        payload = {
            "organic_results": [
                {
                    "title": "Example Labs — Contact us",
                    "snippet": (
                        "Example Labs reception / switchboard. "
                        "Main office phone +91 80412 34567."
                    ),
                }
            ]
        }
        self.assertIsNone(
            discover_public_professional_phone(person(), payload)
        )

    def test_company_only_result_without_person_name_is_ignored(self):
        payload = {
            "organic_results": [
                {
                    "title": "Example Labs corporate office",
                    "snippet": "Business phone +91 80412 34567.",
                }
            ]
        }
        self.assertIsNone(
            discover_public_professional_phone(person(), payload)
        )


class PhoneEnrichmentRouteTests(unittest.TestCase):
    def setUp(self):
        clear_people_cache()
        store_people([person()])

    def tearDown(self):
        clear_people_cache()

    def test_discovered_number_is_public_web_and_does_not_call_hunar(self):
        payload = {"organic_results": [ASSOCIATED_RESULT]}

        with patch(
            "app.routes.people.get_people_provider",
            return_value=SerpApiProvider(),
        ):
            with patch(
                "app.services.people.serpapi.google_search",
                return_value=payload,
            ) as mocked_search:
                with patch(
                    "app.services.outreach_hunar.create_outreach_call"
                ) as mocked_call:
                    first = client.get("/api/people/serpapi:test-person")
                    second = client.get("/api/people/serpapi:test-person")

        self.assertEqual(first.status_code, 200)
        body = first.json()
        self.assertEqual(body["phone"], "+919876543210")
        self.assertEqual(body["public_phone"], "+919876543210")
        self.assertEqual(body["phone_source"], PHONE_SOURCE_PUBLIC_WEB)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(mocked_search.call_count, 1)
        mocked_call.assert_not_called()

    def test_recruiter_provided_number_still_works(self):
        with patch(
            "app.routes.people.get_people_provider",
            return_value=SerpApiProvider(),
        ):
            with patch(
                "app.services.people.serpapi.google_search",
                return_value={"organic_results": []},
            ):
                client.get("/api/people/serpapi:test-person")

        saved = client.put(
            "/api/people/serpapi:test-person/phone",
            json={"phone": "+91 99887 76655"},
        )

        self.assertEqual(saved.status_code, 200)
        body = saved.json()
        self.assertEqual(body["phone"], "+919988776655")
        self.assertEqual(body["phone_source"], PHONE_SOURCE_RECRUITER)

    def test_enrichment_query_is_targeted(self):
        query = build_phone_discovery_query(person())
        self.assertIn('"Anita Sharma"', query)
        self.assertIn('"Example Labs"', query)
        self.assertIn("work phone", query)

    def test_assignment_1_routes_still_registered(self):
        spec = client.get("/openapi.json").json()["paths"]
        self.assertIn("/api/interviews/start", spec)
        self.assertIn("/api/webhooks/hunar", spec)
        self.assertIn("post", spec["/api/interviews/start"])
        self.assertIn("post", spec["/api/webhooks/hunar"])


if __name__ == "__main__":
    unittest.main()
