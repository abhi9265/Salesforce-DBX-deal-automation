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
    """Deterministic local stand-in for the downstream registration contract."""

    REQUIRED_FIELDS = (
        "customer_name",
        "deal_name",
        "country",
        "deal_amount",
        "industry",
        "partner_name",
        "expected_close_date",
    )

    def submit(self, payload: Mapping[str, Any], request_id: UUID) -> RegistrationResult:
        missing = [field for field in self.REQUIRED_FIELDS if not payload.get(field)]
        if missing:
            return RegistrationResult(
                accepted=False,
                message=f"Missing required fields: {', '.join(missing)}",
            )
        return RegistrationResult(
            accepted=True,
            registration_number=f"DBX-{str(request_id)[:8].upper()}",
            message="Mock registration accepted",
        )
