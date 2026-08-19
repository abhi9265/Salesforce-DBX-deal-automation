from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4


class AuditRepository:
    """SQLite-backed audit store for local development and demos.

    Production implementations can use the same repository contract with a
    managed database or Databricks-backed audit table.
    """

    def __init__(self, database_path: str | Path = "data/audit.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS registration_events (
                    event_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    opportunity_id TEXT NOT NULL,
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    actor TEXT,
                    reason TEXT,
                    event_time TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_registration_events_request ON registration_events(request_id)"
            )

    def record_transition(
        self,
        request_id: UUID | str,
        opportunity_id: str,
        from_status: str | None,
        to_status: str,
        actor: str | None = None,
        reason: str | None = None,
    ) -> str:
        event_id = str(uuid4())
        event_time = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO registration_events
                (event_id, request_id, opportunity_id, from_status, to_status, actor, reason, event_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (event_id, str(request_id), opportunity_id, from_status, to_status, actor, reason, event_time),
            )
        return event_id

    def history(self, request_id: UUID | str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM registration_events WHERE request_id = ? ORDER BY event_time, event_id",
                (str(request_id),),
            ).fetchall()
        return [dict(row) for row in rows]
