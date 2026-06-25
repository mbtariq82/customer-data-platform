from __future__ import annotations

from datetime import UTC, datetime

from customer_data_platform.domain import CustomerEvent, EventType
from customer_data_platform.identity import IdentityService
from customer_data_platform.ingestion import EventIngestionService
from customer_data_platform.repository import CustomerRepository


def test_ingests_events_in_batches_and_resolves_identity() -> None:
    repository = CustomerRepository()
    identity = IdentityService(repository)
    ingestion = EventIngestionService(repository, identity, batch_size=2)
    first = ingestion.ingest(
        CustomerEvent(
            event_type=EventType.PAGE_VIEW,
            anonymous_id="anon-1",
            email=None,
            phone=None,
            cookie_id="cookie-1",
            properties={"path": "/pricing"},
            occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    second = ingestion.ingest(
        CustomerEvent(
            event_type=EventType.PURCHASE,
            anonymous_id=None,
            email="buyer@example.com",
            phone=None,
            cookie_id="cookie-1",
            properties={"amount": "99", "category": "training"},
            occurred_at=datetime(2026, 1, 2, tzinfo=UTC),
        )
    )

    assert first.profile_id == second.profile_id
    assert len(repository.list_events()) == 2
    profile = repository.get_profile(first.profile_id)
    assert profile.identifiers["email"] == {"buyer@example.com"}
    assert profile.identifiers["cookie_id"] == {"cookie-1"}
    assert repository.list_audit(profile.id)
