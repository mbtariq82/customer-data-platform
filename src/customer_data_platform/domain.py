from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class PlatformError(Exception):
    pass


class NotFoundError(PlatformError):
    pass


class ValidationError(PlatformError):
    pass


class EventType(StrEnum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    PURCHASE = "purchase"
    CONSENT_CHANGED = "consent_changed"


@dataclass
class CustomerEvent:
    event_type: EventType
    anonymous_id: str | None
    email: str | None
    phone: str | None
    cookie_id: str | None
    properties: dict[str, str]
    occurred_at: datetime
    profile_id: str | None = None
    id: str = field(default_factory=lambda: new_id("evt"))
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class CustomerProfile:
    identifiers: dict[str, set[str]] = field(default_factory=dict)
    traits: dict[str, str] = field(default_factory=dict)
    consent: bool = True
    segment_ids: set[str] = field(default_factory=set)
    id: str = field(default_factory=lambda: new_id("profile"))
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class SegmentRule:
    field: str
    operator: str
    value: str


@dataclass
class Segment:
    name: str
    rules: list[SegmentRule]
    id: str = field(default_factory=lambda: new_id("segment"))
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class AuditEntry:
    action: str
    profile_id: str | None
    details: dict[str, str]
    id: str = field(default_factory=lambda: new_id("audit"))
    created_at: datetime = field(default_factory=utcnow)
