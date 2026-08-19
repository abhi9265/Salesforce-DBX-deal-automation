from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from audit.models import RegistrationEvent
from domain.models import RegistrationRequest


class AuditRepositoryComplete:
    """Complete local repository: materialized request state + immutable events."""

    def __init__(self, path: str | Path = "data/registrations.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS registration_requests (
                    request_id TEXT PRIMARY KEY,
                    opportunity_id TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    validation_errors TEXT NOT NULL DEFAULT '[]',
                    approved_by TEXT, approved_at TEXT,
                    registration_number TEXT, submitted_at TEXT, error TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS registration_events (
                    event_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    opportunity_id TEXT NOT NULL,
                    from_status TEXT NOT NULL,
                    to_status TEXT NOT NULL,
                    actor TEXT, reason TEXT, occurred_at TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_events_request
                    ON registration_events(request_id, occurred_at);
                """
            )

    def save_request(self, request: RegistrationRequest) -> None:
        p = request.to_dict()
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """INSERT INTO registration_requests
                (request_id, opportunity_id, status, validation_errors, approved_by,
                 approved_at, registration_number, submitted_at, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET status=excluded.status,
                validation_errors=excluded.validation_errors, approved_by=excluded.approved_by,
                approved_at=excluded.approved_at, registration_number=excluded.registration_number,
                submitted_at=excluded.submitted_at, error=excluded.error,
                updated_at=CURRENT_TIMESTAMP""",
                (p["request_id"], p["opportunity_id"], p["status"],
                 json.dumps(p["validation_errors"]), p["approved_by"], p["approved_at"],
                 p["registration_number"], p["submitted_at"], p["error"]),
            )

    def record_transition(self, request_id: UUID, opportunity_id: str,
                          from_status: str, to_status: str, *, actor: str | None = None,
                          reason: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        event = RegistrationEvent.now(
            event_id=uuid4(), request_id=request_id, opportunity_id=opportunity_id,
            from_status=from_status, to_status=to_status, actor=actor,
            reason=reason, metadata=metadata,
        )
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """INSERT INTO registration_events
                (event_id, request_id, opportunity_id, from_status, to_status,
                 actor, reason, occurred_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(event.event_id), str(event.request_id), event.opportunity_id,
                 event.from_status, event.to_status, event.actor, event.reason,
                 event.occurred_at, json.dumps(event.metadata)),
            )

    def get_request(self, request_id: UUID) -> sqlite3.Row | None:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                "SELECT * FROM registration_requests WHERE request_id = ?", (str(request_id),)
            ).fetchone()

    def list_events(self, request_id: UUID) -> list[sqlite3.Row]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return list(conn.execute(
                "SELECT * FROM registration_events WHERE request_id = ? ORDER BY occurred_at, rowid",
                (str(request_id),)
            ))
