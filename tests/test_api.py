from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from customer_data_platform.main import create_app


def test_api_ingests_event_evaluates_segment_and_exports_profile() -> None:
    client = TestClient(create_app())
    now = datetime(2026, 6, 25, tzinfo=UTC)
    event = client.post(
        "/events",
        json={
            "event_type": "purchase",
            "email": "buyer@example.com",
            "cookie_id": "cookie-1",
            "properties": {"amount": "99", "category": "training"},
            "occurred_at": (now - timedelta(days=2)).isoformat(),
        },
    )
    assert event.status_code == 202
    profile_id = event.json()["profile_id"]
    segment = client.post(
        "/segments",
        json={
            "name": "Recent training buyers",
            "rules": [
                {"field": "purchased_within_days", "operator": "==", "value": "30"},
                {"field": "property.category", "operator": "==", "value": "training"},
            ],
        },
    )
    assert segment.status_code == 201

    profile = client.post(f"/profiles/{profile_id}/segments/evaluate")
    exported = client.get(f"/profiles/{profile_id}/export")

    assert profile.status_code == 200
    assert segment.json()["id"] in profile.json()["segment_ids"]
    assert exported.status_code == 200
    assert len(exported.json()["events"]) == 1


def test_api_updates_consent_and_deletes_profile_data() -> None:
    client = TestClient(create_app())
    event = client.post(
        "/events",
        json={
            "event_type": "page_view",
            "anonymous_id": "anon-1",
            "properties": {"path": "/"},
            "occurred_at": datetime(2026, 1, 1, tzinfo=UTC).isoformat(),
        },
    )
    profile_id = event.json()["profile_id"]

    consent = client.post(f"/profiles/{profile_id}/consent", json={"consent": False})
    deleted = client.delete(f"/profiles/{profile_id}")
    missing = client.get(f"/profiles/{profile_id}")

    assert consent.status_code == 200
    assert consent.json()["consent"] is False
    assert deleted.status_code == 200
    assert missing.status_code == 404
