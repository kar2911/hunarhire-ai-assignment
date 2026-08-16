import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.people.base import NormalizedPerson
from app.services.people.cache import clear_people_cache, store_people
from app.services.people.enrichment import (
    extract_education,
    extract_experience,
    extract_fields_from_payload,
    extract_location,
    extract_skills,
    enrich_person_from_payloads,
)
from app.services.people.phone import PHONE_SOURCE_RECRUITER
from app.services.people.serpapi import SerpApiProvider


client = TestClient(app)


PROFILE_PAYLOAD = {
    "organic_results": [
        {
            "title": "Anita Sharma - Engineering Manager - Example Labs | LinkedIn",
            "snippet": (
                "Bengaluru, Karnataka, India · 500+ connections. "
                "Engineering Manager at Example Labs. Previously Senior "
                "Software Engineer at Acme Cloud (2019 - 2023). "
                "Education: Bachelor of Technology (BTech), Computer Science "
                "from IIT Madras. Skills: Python, FastAPI, Docker."
            ),
            "rich_snippet": {
                "top": {
                    "detected_extensions": {
                        "location": "Bengaluru, India",
                    }
                }
            },
            "sitelinks": {
                "inline": [
                    {"title": "Experience", "snippet": "Engineering Manager at Example Labs"},
                ]
            },
        }
    ]
}

EDUCATION_PAYLOAD = {
    "organic_results": [
        {
            "title": "Anita Sharma - Education | LinkedIn",
            "snippet": (
                "B.Tech in Computer Science and Engineering from IIT Madras "
                "2014 - 2018"
            ),
        }
    ]
}

EMPTY_PAYLOAD = {"organic_results": []}


def sample_person(**overrides) -> NormalizedPerson:
    data = {
        "id": "serpapi:anita",
        "provider": "serpapi",
        "provider_id": "anita",
        "full_name": "Anita Sharma",
        "first_name": "Anita",
        "last_name": "Sharma",
        "job_title": "Engineering Manager",
        "company_name": "Example Labs",
        "linkedin_url": "https://www.linkedin.com/in/anita-sharma",
        "location": None,
        "skills": [],
        "experience": [],
        "education": [],
        "phone": None,
        "phone_source": None,
        "public_phone": None,
    }
    data.update(overrides)
    return NormalizedPerson(**data)


class EducationExtractionTests(unittest.TestCase):
    def test_btech_computer_science_from_parenthetical(self):
        items = extract_education(
            "Bachelor of Technology (BTech), Computer Science from IIT Madras"
        )
        self.assertTrue(items)
        self.assertEqual(items[0].degree, "B.Tech")
        self.assertEqual(items[0].field, "Computer Science")
        self.assertIn("IIT Madras", items[0].school or "")

    def test_btech_in_cse(self):
        items = extract_education(
            "B.Tech in Computer Science and Engineering from IIT Madras"
        )
        self.assertTrue(items)
        self.assertEqual(items[0].degree, "B.Tech")
        self.assertEqual(items[0].field, "Computer Science and Engineering")

    def test_does_not_infer_degree_from_job_title(self):
        items = extract_education(
            "Anita Sharma is a Senior Software Engineer at Example Labs."
        )
        self.assertEqual(items, [])


class ExperienceExtractionTests(unittest.TestCase):
    def test_multiple_roles(self):
        text = (
            "Engineering Manager at Example Labs · Jan 2023 - Present. "
            "Senior Software Engineer at Acme Cloud 2019 - 2023."
        )
        items = extract_experience(text)
        self.assertGreaterEqual(len(items), 2)
        titles = {item.title for item in items}
        companies = {item.company for item in items}
        self.assertIn("Engineering Manager", titles)
        self.assertIn("Senior Software Engineer", titles)
        self.assertIn("Example Labs", companies)
        self.assertIn("Acme Cloud", companies)


class SkillsLocationTests(unittest.TestCase):
    def test_skills_from_labeled_list_only(self):
        skills = extract_skills("Skills: Python, FastAPI, Docker")
        self.assertIn("Python", skills)
        self.assertIn("FastAPI", skills)
        self.assertIn("Docker", skills)

    def test_does_not_treat_query_echo_as_skills(self):
        skills = extract_skills(
            "site:linkedin.com/in/anita Python FastAPI skills"
        )
        self.assertEqual(skills, [])

    def test_location_from_connections_line(self):
        location = extract_location(
            "Bengaluru, Karnataka, India · 500+ connections"
        )
        self.assertEqual(location, "Bengaluru, Karnataka, India")

    def test_location_ignores_job_title_noise(self):
        location = extract_location(
            "Senior Python Developer ... Bengaluru"
        )
        self.assertIsNotNone(location)
        self.assertNotIn("Developer", location or "")
        self.assertIn("Bengaluru", location or "")

    def test_pipe_separated_headline_skills(self):
        skills = extract_skills(
            "Senior Python Backend Developer | Django | FastAPI | PostgreSQL"
        )
        self.assertIn("Django", skills)
        self.assertIn("FastAPI", skills)
        self.assertIn("PostgreSQL", skills)


class NoFabricationTests(unittest.TestCase):
    def test_empty_serp_does_not_fill_fields(self):
        extracted = extract_fields_from_payload(EMPTY_PAYLOAD)
        self.assertIsNone(extracted["location"])
        self.assertEqual(extracted["skills"], [])
        self.assertEqual(extracted["experience"], [])
        self.assertEqual(extracted["education"], [])
        self.assertIsNone(extracted["email"])


class RecruiterPhoneOverrideTests(unittest.TestCase):
    def test_recruiter_phone_not_replaced_by_public_number(self):
        seeded = sample_person(
            phone="+919988776655",
            phone_source=PHONE_SOURCE_RECRUITER,
        )
        contact = {
            "organic_results": [
                {
                    "title": "Anita Sharma — Engineering Manager at Example Labs",
                    "snippet": (
                        "Office contact for Anita Sharma, Engineering Manager. "
                        "Work phone +91 98765 43210."
                    ),
                }
            ]
        }
        updated = enrich_person_from_payloads(
            seeded,
            [("contact", contact)],
        )
        self.assertEqual(updated.phone, "+919988776655")
        self.assertEqual(updated.phone_source, PHONE_SOURCE_RECRUITER)
        self.assertEqual(updated.public_phone, "+919876543210")


class EnrichmentRouteCacheTests(unittest.TestCase):
    def setUp(self):
        clear_people_cache()
        store_people([sample_person()])

    def tearDown(self):
        clear_people_cache()

    def test_profile_enrichment_is_cached(self):
        with patch(
            "app.routes.people.get_people_provider",
            return_value=SerpApiProvider(),
        ):
            with patch(
                "app.services.people.serpapi.google_search",
                return_value=PROFILE_PAYLOAD,
            ) as mocked_search:
                first = client.get("/api/people/serpapi:anita")
                count_after_first = mocked_search.call_count
                second = client.get("/api/people/serpapi:anita")

        self.assertEqual(first.status_code, 200)
        body = first.json()
        self.assertEqual(body["location"], "Bengaluru, Karnataka, India")
        self.assertTrue(body["education"])
        self.assertEqual(body["education"][0]["degree"], "B.Tech")
        self.assertIn("Python", body["skills"])
        self.assertGreaterEqual(len(body["experience"]), 1)
        self.assertEqual(second.status_code, 200)
        self.assertLessEqual(count_after_first, 5)
        self.assertGreaterEqual(count_after_first, 1)
        self.assertEqual(mocked_search.call_count, count_after_first)

    def test_recruiter_override_via_api(self):
        with patch(
            "app.routes.people.get_people_provider",
            return_value=SerpApiProvider(),
        ):
            with patch(
                "app.services.people.serpapi.google_search",
                return_value=EMPTY_PAYLOAD,
            ):
                client.get("/api/people/serpapi:anita")

        saved = client.put(
            "/api/people/serpapi:anita/phone",
            json={"phone": "+91 99887 76655"},
        )
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()["phone_source"], PHONE_SOURCE_RECRUITER)
        self.assertEqual(saved.json()["phone"], "+919988776655")


if __name__ == "__main__":
    unittest.main()
