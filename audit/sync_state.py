from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


class SyncStateRepository:
    """Stores the last successfully committed source watermark."""

    def __init__(self, path: str | Path = "data/registrations.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS sync_state (source TEXT PRIMARY KEY, watermark TEXT)"
            )

    def get_watermark(self, source: str) -> datetime | None:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT watermark FROM sync_state WHERE source = ?", (source,)
            ).fetchone()
        return datetime.fromisoformat(row[0]) if row and row[0] else None

    def commit_watermark(self, source: str, watermark: datetime) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """INSERT INTO sync_state(source, watermark) VALUES (?, ?)
                ON CONFLICT(source) DO UPDATE SET watermark=excluded.watermark""",
                (source, watermark.isoformat()),
            )
