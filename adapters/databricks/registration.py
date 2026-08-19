from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    accepted: bool
    registration_number: str | None = None
    message: str | None = None


class DatabricksRegistrationAdapter:
    """Draft downstream contract; replace implementation with the authorized DBX interface."""

    def submit(self, payload: Mapping[str, Any], request_id: UUID) -> RegistrationResult:
        if not payload.get("customer_name") or not payload.get("deal_name"):
            return RegistrationResult(False, message="Draft contract requires customer_name and deal_name")
        return RegistrationResult(
            accepted=True,
            registration_number=f"DBX-{str(request_id)[:8].upper()}",
            message="Mock registration accepted",
        )
