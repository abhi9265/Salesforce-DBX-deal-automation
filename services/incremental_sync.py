from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from domain.models import Deal


class DealSource(Protocol):
    def fetch_updated_since(self, watermark: datetime | None) -> list[Deal]: ...


@dataclass(frozen=True, slots=True)
class SyncResult:
    deals: list[Deal]
    next_watermark: datetime | None


def sync_incremental(source: DealSource, watermark: datetime | None) -> SyncResult:
    """Fetch changes after the last successful watermark.

    The caller commits ``next_watermark`` only after downstream processing succeeds.
    """
    deals = source.fetch_updated_since(watermark)
    timestamps = [deal.source_updated_at for deal in deals if deal.source_updated_at]
    next_watermark = max(timestamps) if timestamps else watermark
    return SyncResult(deals=deals, next_watermark=next_watermark)
