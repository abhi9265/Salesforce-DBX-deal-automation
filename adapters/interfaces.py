from __future__ import annotations

from typing import Protocol, Sequence

from domain.models import Deal


class OpportunitySource(Protocol):
    def list_opportunities(self) -> Sequence[Deal]:
        ...


class RegistrationDestination(Protocol):
    def submit(self, deal: Deal) -> str | None:
        """Return an external registration number when confirmed, else None."""
        ...


class RegistrationResultStore(Protocol):
    def record(self, opportunity_id: str, status: str, registration_number: str | None = None) -> None:
        ...
