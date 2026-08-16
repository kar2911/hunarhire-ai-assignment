import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.people.demo import (
    DemoPeopleProvider,
    load_demo_people,
    record_to_person,
)
from app.services.people.base import SearchCriteria
from app.services.people.extract import extract_search_criteria


class DemoProviderTests(unittest.TestCase):
    def test_loads_fifteen_demo_candidates(self):
        people = load_demo_people()
        self.assertEqual(len(people), 15)
        self.assertTrue(all(person.provider == "demo" for person in people))
        self.assertTrue(
            all(person.phone_source == "demo_data" for person in people)
        )
        self.assertTrue(all(person.public_phone is None for person in people))
        self.assertTrue(all(person.linkedin_url is None for person in people))

    def test_placeholder_records_are_skipped(self):
        person = record_to_person(
            {
                "id": "demo-001",
                "name": "Replace with candidate name",
                "current_title": "Engineer",
            },
            0,
        )
        self.assertIsNone(person)

    def test_demo_phone_is_not_public_web(self):
        person = record_to_person(
            {
                "id": "demo-alpha",
                "name": "Demo Candidate Alpha",
                "current_title": "Backend Engineer",
                "phone": "+919999999999",
                "phone_source": "demo_data",
                "email": "alpha@example.com",
            },
            0,
        )
        self.assertIsNotNone(person)
        assert person is not None
        self.assertEqual(person.phone, "+919999999999")
        self.assertIsNone(person.public_phone)
        self.assertEqual(person.phone_source, "demo_data")

    def test_search_reads_temporary_records_file(self):
        payload = [
            {
                "id": "demo-beta",
                "name": "Demo Candidate Beta",
                "current_title": "Python Developer",
                "skills": ["Python", "FastAPI"],
                "phone": "+919888888888",
                "phone_source": "demo_data",
            }
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "demo_records.json"
            path.write_text(json.dumps(payload))

            with patch(
                "app.services.people.demo.DEMO_RECORDS_PATH",
                path,
            ):
                results = DemoPeopleProvider().search_people(
                    SearchCriteria(job_title="Python Developer"),
                    limit=10,
                )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider, "demo")
        self.assertIsNone(results[0].public_phone)

    def test_python_jd_does_not_return_everyone(self):
        criteria = extract_search_criteria(
            "Looking for a Python Developer with FastAPI and AWS experience."
        )
        results = DemoPeopleProvider().search_people(criteria, limit=15)
        titles = {person.job_title for person in results}
        names = [person.full_name for person in results]
        self.assertLess(len(results), 15)
        self.assertIn("Python Developer", titles)
        self.assertNotIn("DevOps Engineer", titles)
        self.assertNotIn("Testing Engineer", titles)
        self.assertTrue(names.index("Jishan") < names.index("Nitesh"))

    def test_devops_jd_returns_devops_only(self):
        criteria = extract_search_criteria(
            "Looking for a DevOps Engineer with AWS, Docker and Kubernetes."
        )
        results = DemoPeopleProvider().search_people(criteria, limit=15)
        titles = {person.job_title for person in results}
        self.assertEqual(titles, {"DevOps Engineer"})
        self.assertEqual(len(results), 2)

    def test_full_stack_jd(self):
        criteria = extract_search_criteria(
            "Looking for a Full Stack Developer with React and TypeScript."
        )
        results = DemoPeopleProvider().search_people(criteria, limit=15)
        titles = {person.job_title for person in results}
        self.assertIn("Full Stack Developer", titles)
        self.assertNotIn("DevOps Engineer", titles)
        self.assertNotIn("Testing Engineer", titles)

    def test_forward_deployed_jd(self):
        criteria = extract_search_criteria(
            "Looking for a Forward Deployed Engineer with Python and LLM skills."
        )
        results = DemoPeopleProvider().search_people(criteria, limit=15)
        titles = {person.job_title for person in results}
        self.assertEqual(titles, {"Forward Deployed Engineer"})
        self.assertEqual(len(results), 2)

    def test_software_developer_jd(self):
        criteria = extract_search_criteria(
            "Looking for a Software Developer with REST APIs and SQL."
        )
        results = DemoPeopleProvider().search_people(criteria, limit=15)
        titles = {person.job_title for person in results}
        self.assertIn("Software Developer", titles)
        self.assertTrue(
            titles <= {"Software Developer", "Python Developer", "Full Stack Developer"}
        )
        self.assertNotIn("Testing Engineer", titles)

    def test_testing_jd(self):
        criteria = extract_search_criteria(
            "Looking for a Testing Engineer with Selenium and API Testing."
        )
        results = DemoPeopleProvider().search_people(criteria, limit=15)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].full_name, "Shekher Sonar")
        self.assertEqual(results[0].company_name, "Mphasis")
        self.assertTrue(results[0].email)
        self.assertTrue(results[0].phone)
        self.assertTrue(results[0].skills)
        self.assertTrue(results[0].education)
        self.assertTrue(results[0].experience)

    def test_serpapi_provider_name_is_unchanged(self):
        from app.services.people.serpapi import SerpApiProvider

        self.assertEqual(SerpApiProvider.name, "serpapi")
        self.assertNotEqual(DemoPeopleProvider.name, SerpApiProvider.name)


if __name__ == "__main__":
    unittest.main()
