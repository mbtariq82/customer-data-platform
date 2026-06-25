from __future__ import annotations

from datetime import datetime, timedelta

from customer_data_platform.domain import CustomerProfile, EventType, Segment, SegmentRule
from customer_data_platform.repository import CustomerRepository


class SegmentationService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def create_segment(self, name: str, rules: list[SegmentRule]) -> Segment:
        segment = Segment(name=name, rules=rules)
        return self.repository.save_segment(segment)

    def evaluate_profile(
        self,
        profile_id: str,
        now: datetime | None = None,
    ) -> CustomerProfile:
        profile = self.repository.get_profile(profile_id)
        matched_segments = {
            segment.id
            for segment in self.repository.list_segments()
            if self._matches_all(profile_id, segment.rules, now or datetime.now(tz=profile.updated_at.tzinfo))
        }
        profile.segment_ids = matched_segments
        return self.repository.save_profile(profile)

    def _matches_all(
        self,
        profile_id: str,
        rules: list[SegmentRule],
        now: datetime,
    ) -> bool:
        events = self.repository.list_events(profile_id)
        return all(self._matches_rule(events, rule, now) for rule in rules)

    @staticmethod
    def _matches_rule(events, rule: SegmentRule, now: datetime) -> bool:
        if rule.field == "event_type":
            return any(SegmentationService._compare(event.event_type.value, rule.operator, rule.value) for event in events)
        if rule.field.startswith("property."):
            key = rule.field.removeprefix("property.")
            return any(SegmentationService._compare(event.properties.get(key), rule.operator, rule.value) for event in events)
        if rule.field == "purchased_within_days":
            days = int(rule.value)
            cutoff = now - timedelta(days=days)
            return any(event.event_type is EventType.PURCHASE and event.occurred_at >= cutoff for event in events)
        return False

    @staticmethod
    def _compare(actual: str | None, operator: str, expected: str) -> bool:
        if operator == "==":
            return actual == expected
        if operator == "!=":
            return actual != expected
        return False
