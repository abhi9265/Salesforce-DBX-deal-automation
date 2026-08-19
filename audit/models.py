from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegistrationEvent:
    event_id: UUID
    request_id: UUID
    opportunity_id: str
    from_status: str
    to_status: str
    actor: str | None
    reason: str | None
    occurred_at: str
    metadata: dict[str, Any]

    @classmethod
    def now(
        cls,
        *,
        event_id: UUID,
        request_id: UUID,
        opportunity_id: str,
        from_status: str,
        to_status: str,
        actor: str | None = None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "RegistrationEvent":
        return cls(
            event_id=event_id,
            request_id=request_id,
            opportunity_id=opportunity_id,
            from_status=from_status,
            to_status=to_status,
            actor=actor,
            reason=reason,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
