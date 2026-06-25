from __future__ import annotations

from customer_data_platform.domain import CustomerEvent, CustomerProfile, utcnow
from customer_data_platform.repository import CustomerRepository


IDENTIFIER_FIELDS = ("anonymous_id", "email", "phone", "cookie_id")


class IdentityService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def resolve(self, event: CustomerEvent) -> CustomerProfile:
        incoming = self._identifiers_from_event(event)
        matched = [
            profile
            for profile in self.repository.list_profiles()
            if self._overlaps(profile.identifiers, incoming)
        ]
        profile = matched[0] if matched else CustomerProfile()
        for other in matched[1:]:
            self._merge(profile, other)
        for key, values in incoming.items():
            profile.identifiers.setdefault(key, set()).update(values)
        profile.updated_at = utcnow()
        return self.repository.save_profile(profile)

    @staticmethod
    def _identifiers_from_event(event: CustomerEvent) -> dict[str, set[str]]:
        identifiers: dict[str, set[str]] = {}
        for field in IDENTIFIER_FIELDS:
            value = getattr(event, field)
            if value:
                identifiers.setdefault(field, set()).add(value.lower())
        return identifiers

    @staticmethod
    def _overlaps(existing: dict[str, set[str]], incoming: dict[str, set[str]]) -> bool:
        return any(existing.get(key, set()) & values for key, values in incoming.items())

    @staticmethod
    def _merge(target: CustomerProfile, source: CustomerProfile) -> None:
        for key, values in source.identifiers.items():
            target.identifiers.setdefault(key, set()).update(values)
        target.traits.update(source.traits)
        target.segment_ids.update(source.segment_ids)
        target.consent = target.consent and source.consent
