from __future__ import annotations

from datetime import UTC, datetime

import pytest

from customer_data_platform.compliance import ComplianceService
from customer_data_platform.domain import CustomerEvent, EventType, NotFoundError
from customer_data_platform.identity import IdentityService
from customer_data_platform.ingestion import EventIngestionService
from customer_data_platform.repository import CustomerRepository


def test_exports_profile_data_and_deletes_subject_data() -> None:
    repository = CustomerRepository()
    identity = IdentityService(repository)
    ingestion = EventIngestionService(repository, identity, batch_size=1)
    compliance = ComplianceService(repository)
    event = ingestion.ingest(
        CustomerEvent(
            event_type=EventType.PAGE_VIEW,
            anonymous_id="anon-1",
            email="user@example.com",
            phone=None,
            cookie_id="cookie-1",
            properties={"path": "/"},
            occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    ingestion.flush()

    compliance.update_consent(event.profile_id, False)
    exported = compliance.export_profile(event.profile_id)
    compliance.delete_profile(event.profile_id)

    assert exported["profile"].consent is False
    assert len(exported["events"]) == 1
    with pytest.raises(NotFoundError):
        repository.get_profile(event.profile_id)
    assert repository.list_events(event.profile_id) == []
    assert any(entry.action == "data_deleted" for entry in repository.list_audit())
