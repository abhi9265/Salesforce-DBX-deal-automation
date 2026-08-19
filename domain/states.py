from __future__ import annotations

from enum import StrEnum

from domain.exceptions import InvalidTransitionError


class RegistrationStatus(StrEnum):
    NEW = "NEW"
    ELIGIBLE = "ELIGIBLE"
    VALIDATED = "VALIDATED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    SUBMITTED = "SUBMITTED"
    REGISTERED = "REGISTERED"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    REJECTED = "REJECTED"
    SUBMISSION_FAILED = "SUBMISSION_FAILED"
    SUBMISSION_UNKNOWN = "SUBMISSION_UNKNOWN"


ALLOWED_TRANSITIONS: dict[RegistrationStatus, set[RegistrationStatus]] = {
    RegistrationStatus.NEW: {RegistrationStatus.ELIGIBLE, RegistrationStatus.NOT_ELIGIBLE},
    RegistrationStatus.ELIGIBLE: {RegistrationStatus.VALIDATED, RegistrationStatus.VALIDATION_FAILED},
    RegistrationStatus.VALIDATED: {RegistrationStatus.READY_FOR_REVIEW, RegistrationStatus.VALIDATION_FAILED},
    RegistrationStatus.READY_FOR_REVIEW: {RegistrationStatus.APPROVED, RegistrationStatus.REJECTED},
    RegistrationStatus.APPROVED: {
        RegistrationStatus.SUBMITTED,
        RegistrationStatus.SUBMISSION_FAILED,
        RegistrationStatus.SUBMISSION_UNKNOWN,
    },
    RegistrationStatus.SUBMITTED: {RegistrationStatus.REGISTERED, RegistrationStatus.SUBMISSION_FAILED, RegistrationStatus.SUBMISSION_UNKNOWN},
    RegistrationStatus.NOT_ELIGIBLE: set(),
    RegistrationStatus.VALIDATION_FAILED: set(),
    RegistrationStatus.REJECTED: set(),
    RegistrationStatus.SUBMISSION_FAILED: set(),
    RegistrationStatus.SUBMISSION_UNKNOWN: set(),
    RegistrationStatus.REGISTERED: set(),
}


def assert_transition(current: RegistrationStatus, target: RegistrationStatus) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidTransitionError(f"Invalid registration transition: {current} -> {target}")
