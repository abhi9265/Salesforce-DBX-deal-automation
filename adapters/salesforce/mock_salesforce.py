from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from domain.models import Deal


class MockSalesforceAdapter:
    """Deterministic local Salesforce source used by the MVP and test suite."""

    def __init__(self, source: Path | list[dict[str, Any]] | None = None) -> None:
        self.source = source or []

    def _records(self) -> list[dict[str, Any]]:
        if isinstance(self.source, Path):
            with self.source.open(newline="", encoding="utf-8") as handle:
                return list(csv.DictReader(handle))
        return list(self.source)

    def list_opportunities(self) -> list[Deal]:
        return [Deal.from_salesforce_row(record) for record in self._records()]

    def fetch_opportunities(self) -> list[Deal]:
        return self.list_opportunities()

    def fetch_updated_since(self, watermark: datetime | None) -> list[Deal]:
        deals = self.list_opportunities()
        if watermark is None:
            return deals
        return [
            deal
            for deal in deals
            if deal.source_updated_at is not None and deal.source_updated_at > watermark
        ]
