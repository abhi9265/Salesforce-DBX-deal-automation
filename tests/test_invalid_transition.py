import pytest

from domain.exceptions import InvalidTransitionError
from domain.models import RegistrationRequest
from domain.states import RegistrationStatus


def test_approval_cannot_skip_review():
    request = RegistrationRequest(opportunity_id="OPP-001")
    with pytest.raises(InvalidTransitionError):
        request.approve("manager@example.com")


def test_registered_requires_registration_number():
    request = RegistrationRequest(opportunity_id="OPP-001")
    request.transition(RegistrationStatus.ELIGIBLE)
    request.transition(RegistrationStatus.VALIDATED)
    request.transition(RegistrationStatus.READY_FOR_REVIEW)
    request.approve("manager@example.com")
    request.mark_submitted("DBX-123")
    with pytest.raises(Exception):
        request.mark_registered("")
