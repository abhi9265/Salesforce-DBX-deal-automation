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
    unknown: bool = False


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


def approved_request(opportunity_id: str) -> RegistrationRequest:
    request = RegistrationRequest(opportunity_id)
    request.transition(RegistrationStatus.ELIGIBLE)
    request.transition(RegistrationStatus.VALIDATED)
    request.transition(RegistrationStatus.READY_FOR_REVIEW)
    request.approve("manager@example.com")
    return request


def test_successful_submission_reaches_registered_and_persists(tmp_path):
    deal = Deal(
        "OPP-006", "Acme", "Platform", "India", 100.0, "Technology",
        "Databricks", "2026-09-30", True, "Not Registered",
    )
    request = approved_request("OPP-006")
    audit = AuditRepository(tmp_path / "audit.db")

    result = RegistrationProcessor(Store(), Gateway(), audit).process(
        deal, request, {"deal_name": "Platform"}
    )

    assert result.processed is True
    assert request.status == RegistrationStatus.REGISTERED
    assert request.registration_number == "DBX-TEST"
    assert [event["to_status"] for event in audit.list_events(request.request_id)] == [
        "SUBMITTED", "REGISTERED",
    ]


def test_unknown_submission_can_be_retried_with_same_request_id(tmp_path):
    class UnknownThenSuccessGateway:
        def __init__(self):
            self.calls = 0
            self.request_ids = []

        def submit(self, payload, request_id):
            self.calls += 1
            self.request_ids.append(request_id)
            if self.calls == 1:
                return Result(False, registration_number=None, message="timeout", unknown=True)
            return Result(True, registration_number="DBX-RECONCILED")

    deal = Deal(
        "OPP-008", "Acme", "Platform", "India", 100.0, "Technology",
        "Databricks", "2026-09-30", True, "Not Registered",
    )
    request = approved_request("OPP-008")
    audit = AuditRepository(tmp_path / "audit.db")
    gateway = UnknownThenSuccessGateway()
    processor = RegistrationProcessor(Store(), gateway, audit)

    first = processor.process(deal, request, {"deal_name": "Platform"})
    second = processor.retry_unknown(deal, request, {"deal_name": "Platform"})

    assert first.processed is False
    assert request.status == RegistrationStatus.REGISTERED
    assert second.processed is True
    assert gateway.calls == 2
    assert gateway.request_ids[0] == gateway.request_ids[1] == request.request_id
    assert [event["to_status"] for event in audit.list_events(request.request_id)] == [
        "SUBMISSION_UNKNOWN", "SUBMITTED", "REGISTERED",
    ]


def test_failed_submission_is_persisted_and_audited(tmp_path):
    class FailedGateway:
        def submit(self, payload, request_id):
            return Result(False, registration_number=None, message="downstream unavailable")

    deal = Deal(
        "OPP-007", "Acme", "Platform", "India", 100.0, "Technology",
        "Databricks", "2026-09-30", True, "Not Registered",
    )
    request = approved_request("OPP-007")
    audit = AuditRepository(tmp_path / "audit.db")

    result = RegistrationProcessor(Store(), FailedGateway(), audit).process(
        deal, request, {"deal_name": "Platform"}
    )

    assert result.processed is False
    assert request.status == RegistrationStatus.SUBMISSION_FAILED
    assert audit.list_events(request.request_id)[0]["to_status"] == "SUBMISSION_FAILED"
