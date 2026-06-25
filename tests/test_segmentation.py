from __future__ import annotations

from datetime import UTC, datetime, timedelta

from customer_data_platform.domain import CustomerEvent, EventType, SegmentRule
from customer_data_platform.identity import IdentityService
from customer_data_platform.ingestion import EventIngestionService
from customer_data_platform.repository import CustomerRepository
from customer_data_platform.segmentation import SegmentationService


def test_segment_membership_updates_from_ingested_events() -> None:
    repository = CustomerRepository()
    identity = IdentityService(repository)
    ingestion = EventIngestionService(repository, identity, batch_size=1)
    segmentation = SegmentationService(repository)
    segment = segmentation.create_segment(
        "Recent training buyers",
        [
            SegmentRule("purchased_within_days", "==", "30"),
            SegmentRule("property.category", "==", "training"),
        ],
    )
    now = datetime(2026, 1, 31, tzinfo=UTC)
    event = ingestion.ingest(
        CustomerEvent(
            event_type=EventType.PURCHASE,
            anonymous_id=None,
            email="buyer@example.com",
            phone=None,
            cookie_id="cookie-1",
            properties={"amount": "99", "category": "training"},
            occurred_at=now - timedelta(days=2),
        )
    )
    ingestion.flush()

    profile = segmentation.evaluate_profile(event.profile_id, now=now)

    assert profile.segment_ids == {segment.id}
