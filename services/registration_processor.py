from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from domain.models import Deal, RegistrationRequest
from domain.states import RegistrationStatus
from services.idempotency import ProcessedDealStore, deal_fingerprint


class RegistrationGateway(Protocol):
    def submit(self, payload: dict[str, Any], request_id):
        """Submit the mapped payload using the registration request identity."""
        ...


class RegistrationAudit(Protocol):
    def record_transition(
        self,
        request_id,
        opportunity_id: str,
        from_status: str | None,
        to_status: str,
        *,
        actor: str | None = None,
        reason: str | None = None,
    ) -> Any: ...


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    request: RegistrationRequest
    processed: bool
    skipped: bool
    reason: str | None = None


class RegistrationProcessor:
    """Coordinates deterministic, idempotent registration submission."""

    def __init__(
        self,
        store: ProcessedDealStore,
        gateway: RegistrationGateway,
        audit: RegistrationAudit | None = None,
    ) -> None:
        self.store = store
        self.gateway = gateway
        self.audit = audit

    def _record(self, request: RegistrationRequest, previous: RegistrationStatus, reason: str | None = None) -> None:
        if self.audit:
            self.audit.record_transition(
                request.request_id,
                request.opportunity_id,
                previous.value,
                request.status.value,
                reason=reason,
            )

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
            previous = request.status
            request.transition(RegistrationStatus.SUBMISSION_FAILED, reason=getattr(result, "message", "submission_failed"))
            self._record(request, previous, request.error)
            return ProcessingResult(
                request=request,
                processed=False,
                skipped=False,
                reason=request.error,
            )

        previous = request.status
        registration_number = getattr(result, "registration_number", None)
        request.mark_submitted(registration_number)
        self._record(request, previous)

        if registration_number and request.status == RegistrationStatus.SUBMITTED:
            previous = request.status
            request.mark_registered(registration_number)
            self._record(request, previous)

        self.store.mark_processed(deal.opportunity_id, fingerprint)
        return ProcessingResult(request=request, processed=True, skipped=False)
