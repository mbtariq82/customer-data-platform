from __future__ import annotations

from threading import RLock

from customer_data_platform.domain import (
    AuditEntry,
    CustomerEvent,
    CustomerProfile,
    NotFoundError,
    Segment,
)


class CustomerRepository:
    def __init__(self) -> None:
        self._events: dict[str, CustomerEvent] = {}
        self._profiles: dict[str, CustomerProfile] = {}
        self._segments: dict[str, Segment] = {}
        self._audit: list[AuditEntry] = []
        self._lock = RLock()

    def save_event(self, event: CustomerEvent) -> CustomerEvent:
        with self._lock:
            self._events[event.id] = event
            return event

    def list_events(self, profile_id: str | None = None) -> list[CustomerEvent]:
        with self._lock:
            events = list(self._events.values())
        if profile_id:
            return [event for event in events if event.profile_id == profile_id]
        return events

    def save_profile(self, profile: CustomerProfile) -> CustomerProfile:
        with self._lock:
            self._profiles[profile.id] = profile
            return profile

    def get_profile(self, profile_id: str) -> CustomerProfile:
        with self._lock:
            try:
                return self._profiles[profile_id]
            except KeyError as exc:
                raise NotFoundError(f"Profile {profile_id!r} was not found.") from exc

    def list_profiles(self) -> list[CustomerProfile]:
        with self._lock:
            return list(self._profiles.values())

    def save_segment(self, segment: Segment) -> Segment:
        with self._lock:
            self._segments[segment.id] = segment
            return segment

    def list_segments(self) -> list[Segment]:
        with self._lock:
            return list(self._segments.values())

    def add_audit(self, entry: AuditEntry) -> AuditEntry:
        with self._lock:
            self._audit.append(entry)
            return entry

    def list_audit(self, profile_id: str | None = None) -> list[AuditEntry]:
        with self._lock:
            entries = list(self._audit)
        if profile_id:
            return [entry for entry in entries if entry.profile_id == profile_id]
        return entries

    def delete_profile_data(self, profile_id: str) -> None:
        with self._lock:
            self._profiles.pop(profile_id, None)
            self._events = {
                event_id: event
                for event_id, event in self._events.items()
                if event.profile_id != profile_id
            }
