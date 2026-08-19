from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from src.domain.models import Deal


class MockSalesforceAdapter:
    """Local Salesforce stand-in backed by synthetic CSV data."""

    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)

    def list_opportunities(self) -> list[Deal]:
        with self.csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return [Deal.from_salesforce_row(row) for row in reader]

    def update_registration_status(self, opportunity_id: str, status: str) -> bool:
        # The real Salesforce adapter will implement the write-back contract.
        # The mock intentionally does not mutate the source fixture.
        return any(
            deal.opportunity_id == opportunity_id
            for deal in self.list_opportunities()
        )
