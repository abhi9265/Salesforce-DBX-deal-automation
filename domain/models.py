from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from domain.states import RegistrationStatus, assert_transition


@dataclass(slots=True, frozen=True)
class Deal:
    opportunity_id: str
    account_name: str
    opportunity_name: str
    country: str
    amount: float | None
    industry: str
    partner: str
    close_date: str
    registration_required: bool
    registration_status: str
    source_system: str = "mock"
    source_record_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_salesforce_row(cls, row: dict[str, Any]) -> "Deal":
        amount_raw = row.get("Amount")
        try:
            amount = float(amount_raw) if amount_raw not in (None, "") else None
        except (TypeError, ValueError):
            amount = None
        return cls(
            opportunity_id=str(row.get("OpportunityId", "")).strip(),
            account_name=str(row.get("AccountName", "")).strip(),
            opportunity_name=str(row.get("OpportunityName", "")).strip(),
            country=str(row.get("Country", "")).strip(),
            amount=amount,
            industry=str(row.get("Industry", "")).strip(),
            partner=str(row.get("Partner", "")).strip(),
            close_date=str(row.get("CloseDate", "")).strip(),
            registration_required=str(row.get("RegistrationRequired", "")).strip().lower() == "true",
            registration_status=str(row.get("RegistrationStatus", "")).strip(),
            source_system="salesforce-mock",
            source_record_id=str(row.get("OpportunityId", "")).strip(),
            raw=dict(row),
        )


@dataclass(slots=True)
class RegistrationRequest:
    opportunity_id: str
    request_id: UUID = field(default_factory=uuid4)
    status: RegistrationStatus = RegistrationStatus.NEW
    validation_errors: list[str] = field(default_factory=list)
    approved_by: str | None = None
    approved_at: str | None = None
    registration_number: str | None = None
    submitted_at: str | None = None
    error: str | None = None

    def transition(self, target: RegistrationStatus, *, reason: str | None = None) -> None:
        assert_transition(self.status, target)
        self.status = target
        self.error = reason

    def approve(self, approver: str) -> None:
        self.transition(RegistrationStatus.APPROVED)
        self.approved_by = approver
        self.approved_at = datetime.now(timezone.utc).isoformat()

    def mark_submitted(self, registration_number: str | None = None) -> None:
        self.submitted_at = datetime.now(timezone.utc).isoformat()
        self.registration_number = registration_number
        self.transition(
            RegistrationStatus.SUBMITTED if registration_number else RegistrationStatus.SUBMISSION_UNKNOWN
        )

    def mark_registered(self, registration_number: str) -> None:
        if not registration_number:
            raise ValueError("registration_number is required for REGISTERED status")
        self.registration_number = registration_number
        self.transition(RegistrationStatus.REGISTERED)

    def reject(self, reason: str) -> None:
        self.transition(RegistrationStatus.REJECTED, reason=reason)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": str(self.request_id),
            "opportunity_id": self.opportunity_id,
            "status": self.status.value,
            "validation_errors": list(self.validation_errors),
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "registration_number": self.registration_number,
            "submitted_at": self.submitted_at,
            "error": self.error,
        }
