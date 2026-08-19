from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from domain.models import Deal


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    accepted: bool
    registration_number: str | None = None
    error: str | None = None


class MockDatabricksRegistrationAdapter:
    """Local stand-in for the downstream DBX registration contract."""

    def register(self, deal: Deal) -> RegistrationResult:
        if not deal.opportunity_id:
            return RegistrationResult(False, error="Opportunity ID is required")
        return RegistrationResult(True, registration_number=f"DBX-{uuid4().hex[:10].upper()}")
