from datetime import datetime, timezone

from domain.models import Deal
from services.incremental_sync import sync_incremental


def deal(opportunity_id: str, updated: str) -> Deal:
    return Deal(
        opportunity_id=opportunity_id,
        account_name="Acme",
        opportunity_name="Platform",
        country="India",
        amount=100.0,
        industry="Technology",
        partner="Databricks",
        close_date="2026-09-30",
        registration_required=True,
        registration_status="Not Registered",
        source_updated_at=datetime.fromisoformat(updated),
    )


class FakeSource:
    def __init__(self, deals):
        self.deals = deals

    def fetch_updated_since(self, watermark):
        return [d for d in self.deals if watermark is None or d.source_updated_at > watermark]


def test_incremental_sync_returns_changes_and_next_watermark():
    first = deal("OPP-1", "2026-08-19T10:00:00+00:00")
    second = deal("OPP-2", "2026-08-19T11:00:00+00:00")
    result = sync_incremental(FakeSource([first, second]), datetime(2026, 8, 19, 9, tzinfo=timezone.utc))
    assert [d.opportunity_id for d in result.deals] == ["OPP-1", "OPP-2"]
    assert result.next_watermark == second.source_updated_at


def test_watermark_does_not_change_without_records():
    watermark = datetime(2026, 8, 19, 9, tzinfo=timezone.utc)
    result = sync_incremental(FakeSource([]), watermark)
    assert result.deals == []
    assert result.next_watermark == watermark
