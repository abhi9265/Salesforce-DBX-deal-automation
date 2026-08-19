from dataclasses import dataclass

from audit.repository import AuditRepository
from domain.models import Deal, RegistrationRequest
from domain.states import RegistrationStatus
from services.registration_processor import RegistrationProcessor


@dataclass
class Result:
    accepted: bool
    registration_number: str | None = "DBX-TEST"
    message: str = "ok"


class Store:
    def __init__(self):
        self.items = set()

    def has_processed(self, opportunity_id, fingerprint):
        return (opportunity_id, fingerprint) in self.items

    def mark_processed(self, opportunity_id, fingerprint):
        self.items.add((opportunity_id, fingerprint))


class Gateway:
    def submit(self, payload, request_id):
        return Result(True)


def approved_request():
    request = RegistrationRequest("OPP-006")
    request.transition(RegistrationStatus.ELIGIBLE)
    request.transition(RegistrationStatus.VALIDATED)
    request.transition(RegistrationStatus.READY_FOR_REVIEW)
    request.approve("manager@example.com")
    return request


def test_successful_submission_reaches_registered_and_audits(tmp_path):
    deal = Deal("OPP-006", "Acme", "Platform", "India", 100.0, "Technology", "Databricks", "2026-09-30", True, "Not Registered")
    request = approved_request()
    audit = AuditRepository(tmp_path / "audit.db")
    result = RegistrationProcessor(Store(), Gateway(), audit).process(deal, request, {"deal_name": "Platform"})

    assert result.processed is True
    assert request.status == RegistrationStatus.REGISTERED
    assert request.registration_number == "DBX-TEST"
    history = audit.history(request.request_id)
    assert [event["to_status"] for event in history] == ["SUBMITTED", "REGISTERED"]


def test_failed_submission_is_audited(tmp_path):
    class FailedGateway:
        def submit(self, payload, request_id):
            return Result(False, registration_number=None, message="downstream unavailable")

    deal = Deal("OPP-007", "Acme", "Platform", "India", 100.0, "Technology", "Databricks", "2026-09-30", True, "Not Registered")
    request = approved_request()
    request.opportunity_id = "OPP-007"
    audit = AuditRepository(tmp_path / "audit.db")
    result = RegistrationProcessor(Store(), FailedGateway(), audit).process(deal, request, {"deal_name": "Platform"})

    assert result.processed is False
    assert request.status == RegistrationStatus.SUBMISSION_FAILED
    assert audit.history(request.request_id)[0]["to_status"] == "SUBMISSION_FAILED"
