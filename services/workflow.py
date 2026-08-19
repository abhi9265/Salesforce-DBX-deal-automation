from __future__ import annotations

from audit.repository import AuditRepository
from domain.models import Deal, RegistrationRequest
from domain.states import RegistrationStatus
from services.eligibility import is_eligible
from services.validation import validate_deal


class DealRegistrationWorkflow:
    """Coordinates deterministic rules and external adapters."""

    def __init__(self, audit: AuditRepository) -> None:
        self.audit = audit

    def evaluate(self, deal: Deal) -> RegistrationRequest:
        request = RegistrationRequest(opportunity_id=deal.opportunity_id)
        self._transition(request, RegistrationStatus.ELIGIBLE if is_eligible(deal) else RegistrationStatus.NOT_ELIGIBLE)
        if request.status == RegistrationStatus.NOT_ELIGIBLE:
            return request

        errors = validate_deal(deal)
        request.validation_errors = list(errors)
        target = RegistrationStatus.VALIDATED if not errors else RegistrationStatus.VALIDATION_FAILED
        self._transition(request, target, reason="; ".join(errors) if errors else None)
        return request

    def prepare_for_review(self, request: RegistrationRequest) -> RegistrationRequest:
        self._transition(request, RegistrationStatus.READY_FOR_REVIEW)
        return request

    def approve(self, request: RegistrationRequest, approver: str) -> RegistrationRequest:
        previous = request.status
        request.approve(approver)
        self.audit.record_transition(request.request_id, request.opportunity_id, previous.value, request.status.value, approver)
        return request

    def _transition(
        self,
        request: RegistrationRequest,
        target: RegistrationStatus,
        reason: str | None = None,
    ) -> None:
        previous = request.status
        request.transition(target, reason=reason)
        self.audit.record_transition(
            request.request_id,
            request.opportunity_id,
            previous.value,
            target.value,
            reason=reason,
        )
