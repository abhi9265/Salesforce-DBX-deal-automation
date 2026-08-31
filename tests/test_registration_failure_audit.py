from domain.models import Deal, RegistrationRequest
from domain.states import RegistrationStatus
from services.registration_processor import RegistrationProcessor


class MemoryStore:
    def __init__(self):
        self.processed = set()

    def has_processed(self, opportunity_id, fingerprint):
        return (opportunity_id, fingerprint) in self.processed

    def mark_processed(self, opportunity_id, fingerprint):
        self.processed.add((opportunity_id, fingerprint))


class FailingGateway:
    def submit(self, payload, request_id):
        return type("Result", (), {"accepted": False, "message": "retryable downstream failure"})()


def test_failed_submission_is_not_marked_processed(tmp_path):
    from audit.repository import AuditRepository

    deal = Deal(
        opportunity_id="OPP-FAIL-001",
        account_name="Acme",
        opportunity_name="Platform",
        country="India",
        amount=100.0,
        industry="Technology",
        partner="Databricks",
        close_date="2026-09-30",
        registration_required=True,
        registration_status="Not Registered",
    )
    request = RegistrationRequest(deal.opportunity_id)
    request.transition(RegistrationStatus.ELIGIBLE)
    request.transition(RegistrationStatus.VALIDATED)
    request.transition(RegistrationStatus.READY_FOR_REVIEW)
    request.approve("manager@example.com")

    audit = AuditRepository(tmp_path / "audit.db")
    store = MemoryStore()
    result = RegistrationProcessor(store, FailingGateway(), audit=audit).process(
        deal,
        request,
        {"customer_name": "Acme", "deal_name": "Platform"},
    )

    assert result.processed is False
    assert request.status == RegistrationStatus.SUBMISSION_FAILED
    assert store.processed == set()
    history = audit.history(request.request_id)
    assert history[-1]["to_status"] == "SUBMISSION_FAILED"
