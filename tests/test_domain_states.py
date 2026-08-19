import pytest

from domain.exceptions import InvalidTransitionError
from domain.states import RegistrationStatus, assert_transition


def test_happy_path_transition_is_allowed():
    assert_transition(RegistrationStatus.READY_FOR_REVIEW, RegistrationStatus.APPROVED)


def test_invalid_transition_is_rejected():
    with pytest.raises(InvalidTransitionError):
        assert_transition(RegistrationStatus.NEW, RegistrationStatus.APPROVED)
