from __future__ import annotations

from audit.repository import AuditRepository
from domain.models import Deal, RegistrationRequest
from domain.states import RegistrationStatus
from services.eligibility import is_eligible
from services.validation import validate_deal


class DealRegistrationWorkflow:
    """Coordinate deterministic rules and durable workflow events."""

    def __init__(self, audit: AuditRepository) -> None:
        self.audit = audit

    @staticmethod
    def _validation_payload(deal: Deal) -> dict[str, object]:
        return {
            "account_name": deal.account_name,
            "opportunity_name": deal.opportunity_name,
            "country": deal.country,
            "amount": deal.amount,
            "industry": deal.industry,
            "partner": deal.partner,
            "close_date": deal.close_date,
        }

    def evaluate(self, deal: Deal) -> RegistrationRequest:
        request = RegistrationRequest(opportunity_id=deal.opportunity_id)
        target = (
            RegistrationStatus.ELIGIBLE
            if is_eligible(deal)
            else RegistrationStatus.NOT_ELIGIBLE
        )
        self._transition(request, target)
        if request.status == RegistrationStatus.NOT_ELIGIBLE:
            return request

        errors = validate_deal(self._validation_payload(deal))
        request.validation_errors = list(errors)
        target = (
            RegistrationStatus.VALIDATED
            if not errors
            else RegistrationStatus.VALIDATION_FAILED
        )
        self._transition(
            request,
            target,
            reason="; ".join(errors) if errors else None,
        )
        return request

    def prepare_for_review(self, request: RegistrationRequest) -> RegistrationRequest:
        self._transition(request, RegistrationStatus.READY_FOR_REVIEW)
        return request

    def approve(
        self,
        request: RegistrationRequest,
        approver: str,
    ) -> RegistrationRequest:
        previous = request.status
        request.approve(approver)
        self.audit.record_transition(
            request.request_id,
            request.opportunity_id,
            previous.value,
            request.status.value,
            actor=approver,
        )
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
