from __future__ import annotations

from customer_data_platform.domain import AuditEntry, CustomerEvent, EventType, ValidationError
from customer_data_platform.identity import IdentityService
from customer_data_platform.repository import CustomerRepository


class EventIngestionService:
    def __init__(
        self,
        repository: CustomerRepository,
        identity_service: IdentityService,
        batch_size: int = 10,
    ) -> None:
        self.repository = repository
        self.identity_service = identity_service
        self.batch_size = batch_size
        self.buffer: list[CustomerEvent] = []

    def ingest(self, event: CustomerEvent) -> CustomerEvent:
        if not any([event.anonymous_id, event.email, event.phone, event.cookie_id]):
            raise ValidationError("At least one identifier is required.")
        profile = self.identity_service.resolve(event)
        event.profile_id = profile.id
        if event.event_type is EventType.CONSENT_CHANGED:
            profile.consent = event.properties.get("consent", "true").lower() == "true"
            self.repository.save_profile(profile)
        self.buffer.append(event)
        if len(self.buffer) >= self.batch_size:
            self.flush()
        self.repository.add_audit(
            AuditEntry(
                action="event_ingested",
                profile_id=profile.id,
                details={"event_type": event.event_type.value},
            )
        )
        return event

    def flush(self) -> list[CustomerEvent]:
        flushed = [self.repository.save_event(event) for event in self.buffer]
        self.buffer.clear()
        return flushed
