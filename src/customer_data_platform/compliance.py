from __future__ import annotations

from customer_data_platform.domain import AuditEntry
from customer_data_platform.repository import CustomerRepository


class ComplianceService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def export_profile(self, profile_id: str) -> dict[str, object]:
        profile = self.repository.get_profile(profile_id)
        events = self.repository.list_events(profile_id)
        audit = self.repository.list_audit(profile_id)
        self.repository.add_audit(
            AuditEntry(
                action="data_exported",
                profile_id=profile_id,
                details={"event_count": str(len(events))},
            )
        )
        return {
            "profile": profile,
            "events": events,
            "audit": audit,
        }

    def delete_profile(self, profile_id: str) -> None:
        self.repository.get_profile(profile_id)
        self.repository.delete_profile_data(profile_id)
        self.repository.add_audit(
            AuditEntry(
                action="data_deleted",
                profile_id=profile_id,
                details={},
            )
        )

    def update_consent(self, profile_id: str, consent: bool) -> None:
        profile = self.repository.get_profile(profile_id)
        profile.consent = consent
        self.repository.save_profile(profile)
        self.repository.add_audit(
            AuditEntry(
                action="consent_changed",
                profile_id=profile_id,
                details={"consent": str(consent).lower()},
            )
        )
