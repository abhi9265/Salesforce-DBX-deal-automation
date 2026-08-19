from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteProcessedDealStore:
    """Durable local idempotency store for successfully submitted deal versions."""

    def __init__(self, path: str | Path = "data/idempotency.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_deals (
                    opportunity_id TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (opportunity_id, fingerprint)
                )
                """
            )

    def has_processed(self, opportunity_id: str, fingerprint: str) -> bool:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_deals WHERE opportunity_id = ? AND fingerprint = ?",
                (opportunity_id, fingerprint),
            ).fetchone()
        return row is not None

    def mark_processed(self, opportunity_id: str, fingerprint: str) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_deals(opportunity_id, fingerprint) VALUES (?, ?)",
                (opportunity_id, fingerprint),
            )
