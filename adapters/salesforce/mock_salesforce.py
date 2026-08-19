from __future__ import annotations

from datetime import datetime
from typing import Any

from domain.models import Deal


class MockSalesforceAdapter:
    """Deterministic local Salesforce source used by the MVP and test suite."""

    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self.records = records or []

    def fetch_opportunities(self) -> list[Deal]:
        return [Deal.from_salesforce_row(record) for record in self.records]

    def fetch_updated_since(self, watermark: datetime | None) -> list[Deal]:
        deals = self.fetch_opportunities()
        if watermark is None:
            return deals
        return [
            deal for deal in deals
            if deal.source_updated_at is not None and deal.source_updated_at > watermark
        ]
