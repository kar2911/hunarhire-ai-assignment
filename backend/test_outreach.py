import base64
import hashlib
import hmac
import json
import os
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Interview
from app.outreach_models import Outreach
from app.services.people.base import NormalizedPerson
from app.services.people.cache import store_people
from app.services.outreach_hunar import OutreachHunarError

# Isolate from production hunarhire.db. Previous failures were leftover
# rows with fixture call_ids (call-test-success-001, call-webhook-001)
# colliding with UNIQUE(call_id) — a test isolation issue, not a schema bug.
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_outreach.db")
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


client = TestClient(app)

PERSON_ID = "serpapi:outreach-test-person"
VALID_PHONE = "+919876543210"
OUTREACH_AGENT = "a2fa5b24-0dee-4f59-9aa3-3bad9c93dfb3"


def seed_person() -> None:
    store_people(
        [
            NormalizedPerson(
                id=PERSON_ID,
                provider="serpapi",
                provider_id="outreach-test-person",
                full_name="Test Candidate",
                job_title="Senior Python Developer",
                phone=None,
            )
        ]
    )


def sign_body(body: bytes, timestamp: str, api_key: str) -> str:
    digest = hmac.new(
        api_key.encode("utf-8"),
        timestamp.encode("utf-8") + b"." + body,
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


class OutreachBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=test_engine)
        app.dependency_overrides[get_db] = override_get_db

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()

        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def setUp(self):
        seed_person()
        db = TestingSessionLocal()

        try:
            db.query(Outreach).delete()
            db.commit()
        finally:
            db.close()

    def test_missing_person_returns_404(self):
        with patch(
            "app.routes.outreach.HUNAR_OUTREACH_AGENT_ID",
            OUTREACH_AGENT,
        ):
            response = client.post(
                "/api/outreach/call",
                json={
                    "person_id": "serpapi:does-not-exist",
                    "phone": VALID_PHONE,
                },
            )

        self.assertEqual(response.status_code, 404)

    def test_invalid_phone_returns_422(self):
        with patch(
            "app.routes.outreach.HUNAR_OUTREACH_AGENT_ID",
            OUTREACH_AGENT,
        ):
            response = client.post(
                "/api/outreach/call",
                json={
                    "person_id": PERSON_ID,
                    "phone": "9876543210",
                },
            )

        self.assertEqual(response.status_code, 422)

    def test_missing_outreach_agent_returns_503(self):
        with patch("app.routes.outreach.HUNAR_OUTREACH_AGENT_ID", ""):
            response = client.post(
                "/api/outreach/call",
                json={
                    "person_id": PERSON_ID,
                    "phone": VALID_PHONE,
                },
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["detail"],
            "Outreach agent is not configured.",
        )

    def test_mocked_successful_hunar_call_creates_outreach(self):
        hunar_response = {
            "id": "call-test-success-001",
            "status": "NOT_STARTED",
            "lifecycle_status": "NOT_STARTED",
        }

        with patch(
            "app.routes.outreach.HUNAR_OUTREACH_AGENT_ID",
            OUTREACH_AGENT,
        ), patch(
            "app.routes.outreach.create_outreach_call",
            return_value=hunar_response,
        ) as mocked_create:
            response = client.post(
                "/api/outreach/call",
                json={
                    "person_id": PERSON_ID,
                    "phone": VALID_PHONE,
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["call_id"], "call-test-success-001")
        self.assertTrue(payload["request_id"].startswith("outreach-"))
        self.assertEqual(payload["status"], "NOT_STARTED")
        self.assertNotIn("HUNAR_API_KEY", json.dumps(payload))
        self.assertNotIn("X-API-Key", json.dumps(payload))

        kwargs = mocked_create.call_args.kwargs
        self.assertEqual(kwargs["agent_id"], OUTREACH_AGENT)
        self.assertEqual(
            set(kwargs["custom_data"].keys()),
            {"role_title", "questions"},
        )
        self.assertEqual(
            kwargs["custom_data"]["role_title"],
            "Senior Python Developer",
        )
        self.assertIn("Hunar.ai", kwargs["custom_data"]["questions"])
        self.assertIn("open_to_opportunities", kwargs["custom_data"]["questions"])
        self.assertIn("notice_period", kwargs["custom_data"]["questions"])
        self.assertIn("salary_expectation", kwargs["custom_data"]["questions"])
        self.assertNotIn("job_summary", kwargs["custom_data"])
        self.assertNotIn("interview_questions", kwargs["custom_data"])

        db = TestingSessionLocal()
        try:
            row = db.query(Outreach).filter(
                Outreach.call_id == "call-test-success-001"
            ).one()
            interview_match = (
                db.query(Interview)
                .filter(Interview.call_id == "call-test-success-001")
                .first()
            )
            self.assertIsNone(interview_match)
            self.assertEqual(row.person_id, PERSON_ID)
            self.assertEqual(row.request_id, payload["request_id"])
        finally:
            db.close()

    def test_mocked_hunar_failure_marks_outreach_failed(self):
        with patch(
            "app.routes.outreach.HUNAR_OUTREACH_AGENT_ID",
            OUTREACH_AGENT,
        ), patch(
            "app.routes.outreach.create_outreach_call",
            side_effect=OutreachHunarError(
                "Unable to start the outreach call.",
                status_code=422,
            ),
        ):
            response = client.post(
                "/api/outreach/call",
                json={
                    "person_id": PERSON_ID,
                    "phone": VALID_PHONE,
                },
            )

        self.assertEqual(response.status_code, 422)

        db = TestingSessionLocal()
        try:
            row = (
                db.query(Outreach)
                .filter(Outreach.person_id == PERSON_ID)
                .order_by(Outreach.id.desc())
                .first()
            )
            self.assertEqual(row.status, "FAILED")
            self.assertIsNone(row.call_id)
            interview_match = (
                db.query(Interview)
                .filter(Interview.request_id == row.request_id)
                .first()
                if hasattr(Interview, "request_id")
                else None
            )
            self.assertIsNone(interview_match)
        finally:
            db.close()

    def test_signed_outreach_webhook_updates_record(self):
        hunar_response = {
            "id": "call-webhook-001",
            "status": "NOT_STARTED",
            "lifecycle_status": "NOT_STARTED",
        }

        with patch(
            "app.routes.outreach.HUNAR_OUTREACH_AGENT_ID",
            OUTREACH_AGENT,
        ), patch(
            "app.routes.outreach.create_outreach_call",
            return_value=hunar_response,
        ):
            created = client.post(
                "/api/outreach/call",
                json={
                    "person_id": PERSON_ID,
                    "phone": VALID_PHONE,
                },
            ).json()

        from app.config import HUNAR_WEBHOOK_API_KEYS

        payload = {
            "event_type": "call_summary",
            "call_id": created["call_id"],
            "request_id": created["request_id"],
            "status": "COMPLETED",
            "lifecycle_status": "COMPLETED",
            "answered_by": "HUMAN",
            "duration_seconds": 42,
            "recording_url": "https://recordings.example/test.mp3",
            "result": {
                "open_to_opportunities": "Yes",
                "notice_period": "30 days",
                "salary_expectation": "Not disclosed",
            },
        }
        body = json.dumps(payload).encode("utf-8")
        timestamp = str(int(time.time()))
        signature = sign_body(
            body,
            timestamp,
            HUNAR_WEBHOOK_API_KEYS[0],
        )

        response = client.post(
            "/api/webhooks/hunar-outreach",
            content=body,
            headers={
                "X-Hunar-Timestamp": timestamp,
                "X-Hunar-Signature": signature,
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 200)

        detail = client.get(f"/api/outreach/{created['id']}").json()
        self.assertEqual(detail["status"], "COMPLETED")
        self.assertEqual(detail["recording_url"], payload["recording_url"])
        self.assertEqual(detail["answered_by"], "HUMAN")
        self.assertEqual(detail["engagement_status"], "Yes")
        self.assertEqual(
            detail["result"]["open_to_opportunities"],
            "Yes",
        )

        replay = client.post(
            "/api/webhooks/hunar-outreach",
            content=body,
            headers={
                "X-Hunar-Timestamp": timestamp,
                "X-Hunar-Signature": signature,
                "Content-Type": "application/json",
            },
        )
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(
            replay.json()["message"],
            "Webhook already processed",
        )

    def test_invalid_webhook_signature_rejected(self):
        body = json.dumps(
            {"event_type": "call_summary", "call_id": "x"}
        ).encode("utf-8")

        response = client.post(
            "/api/webhooks/hunar-outreach",
            content=body,
            headers={
                "X-Hunar-Timestamp": str(int(time.time())),
                "X-Hunar-Signature": "invalid",
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_stale_webhook_timestamp_rejected(self):
        from app.config import HUNAR_WEBHOOK_API_KEYS

        body = json.dumps(
            {"event_type": "call_summary", "call_id": "x"}
        ).encode("utf-8")
        timestamp = str(int(time.time()) - 400)
        signature = sign_body(body, timestamp, HUNAR_WEBHOOK_API_KEYS[0])

        response = client.post(
            "/api/webhooks/hunar-outreach",
            content=body,
            headers={
                "X-Hunar-Timestamp": timestamp,
                "X-Hunar-Signature": signature,
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_unknown_call_id_acknowledged(self):
        from app.config import HUNAR_WEBHOOK_API_KEYS

        payload = {
            "event_type": "call_summary",
            "call_id": "unknown-call",
            "request_id": "outreach-unknown",
            "status": "COMPLETED",
        }
        body = json.dumps(payload).encode("utf-8")
        timestamp = str(int(time.time()))
        signature = sign_body(body, timestamp, HUNAR_WEBHOOK_API_KEYS[0])

        response = client.post(
            "/api/webhooks/hunar-outreach",
            content=body,
            headers={
                "X-Hunar-Timestamp": timestamp,
                "X-Hunar-Signature": signature,
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Outreach not found")

    def test_assignment_1_routes_still_respond(self):
        health = client.get("/health")
        self.assertEqual(health.status_code, 200)

        interviews = client.get("/api/dashboard/interviews")
        self.assertEqual(interviews.status_code, 200)
        self.assertIsInstance(interviews.json(), list)

        if interviews.json():
            first_id = interviews.json()[0]["id"]
            detail = client.get(f"/api/dashboard/interviews/{first_id}")
            self.assertEqual(detail.status_code, 200)
            self.assertIn("scores", detail.json())

        from app.config import HUNAR_WEBHOOK_API_KEYS

        payload = {
            "event_type": "call_summary",
            "call_id": "not-an-interview",
            "status": "COMPLETED",
        }
        body = json.dumps(payload).encode("utf-8")
        timestamp = str(int(time.time()))
        signature = sign_body(body, timestamp, HUNAR_WEBHOOK_API_KEYS[0])

        a1_webhook = client.post(
            "/api/webhooks/hunar",
            content=body,
            headers={
                "X-Hunar-Timestamp": timestamp,
                "X-Hunar-Signature": signature,
                "Content-Type": "application/json",
            },
        )
        self.assertEqual(a1_webhook.status_code, 200)
        self.assertEqual(
            a1_webhook.json()["message"],
            "Interview not found",
        )


if __name__ == "__main__":
    unittest.main()
