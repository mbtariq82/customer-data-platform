from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from customer_data_platform.domain import EventType


class HealthResponse(BaseModel):
    status: str


class EventRequest(BaseModel):
    event_type: EventType
    anonymous_id: str | None = None
    email: str | None = None
    phone: str | None = None
    cookie_id: str | None = None
    properties: dict[str, str] = Field(default_factory=dict)
    occurred_at: datetime


class SegmentRuleRequest(BaseModel):
    field: str
    operator: str
    value: str


class SegmentRequest(BaseModel):
    name: str = Field(min_length=1)
    rules: list[SegmentRuleRequest]


class ConsentRequest(BaseModel):
    consent: bool


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: EventType
    anonymous_id: str | None
    email: str | None
    phone: str | None
    cookie_id: str | None
    properties: dict[str, str]
    occurred_at: datetime
    profile_id: str | None
    created_at: datetime


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    identifiers: dict[str, set[str]]
    traits: dict[str, str]
    consent: bool
    segment_ids: set[str]
    created_at: datetime
    updated_at: datetime


class SegmentRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    field: str
    operator: str
    value: str


class SegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    rules: list[SegmentRuleResponse]
    created_at: datetime


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    profile_id: str | None
    details: dict[str, str]
    created_at: datetime


class ExportResponse(BaseModel):
    profile: ProfileResponse
    events: list[EventResponse]
    audit: list[AuditResponse]


class DeleteResponse(BaseModel):
    deleted: bool
