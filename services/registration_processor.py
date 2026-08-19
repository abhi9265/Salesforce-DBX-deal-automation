from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from domain.models import Deal, RegistrationRequest
from services.idempotency import ProcessedDealStore, deal_fingerprint


class RegistrationGateway(Protocol):
    def submit(self, payload: dict[str, Any], request_id):
        """Submit the mapped payload using the registration request identity."""
        ...


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    request: RegistrationRequest
    processed: bool
    skipped: bool
    reason: str | None = None


class RegistrationProcessor:
    """Coordinates deterministic, idempotent registration submission."""

    def __init__(self, store: ProcessedDealStore, gateway: RegistrationGateway) -> None:
        self.store = store
        self.gateway = gateway

    def process(self, deal: Deal, request: RegistrationRequest, payload: dict[str, Any]) -> ProcessingResult:
        fingerprint = deal_fingerprint(deal)
        if self.store.has_processed(deal.opportunity_id, fingerprint):
            return ProcessingResult(
                request=request,
                processed=False,
                skipped=True,
                reason="unchanged_source_version",
            )

        result = self.gateway.submit(payload, request.request_id)
        if not getattr(result, "accepted", False):
            return ProcessingResult(
                request=request,
                processed=False,
                skipped=False,
                reason=getattr(result, "message", "submission_failed"),
            )

        self.store.mark_processed(deal.opportunity_id, fingerprint)
        return ProcessingResult(request=request, processed=True, skipped=False)
