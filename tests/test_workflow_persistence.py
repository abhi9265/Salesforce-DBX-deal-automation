from __future__ import annotations

from domain.models import Deal
from services.workflow import DealRegistrationWorkflow
from audit.repository_v2 import AuditRepositoryV2


def test_request_and_event_history_are_persisted(tmp_path):
    audit = AuditRepositoryV2(tmp_path / "registrations.db")
    workflow = DealRegistrationWorkflow(audit)
    deal = Deal(
        opportunity_id="OPP-001",
        account_name="Acme",
        opportunity_name="Acme Data Platform",
        country="India",
        amount=100000.0,
        industry="Technology",
        partner="Databricks",
        close_date="2026-09-30",
        registration_required=True,
        registration_status="Not Registered",
    )

    request = workflow.evaluate(deal)
    audit.save_request(request)
    workflow.prepare_for_review(request)
    audit.save_request(request)
    workflow.approve(request, "manager@example.com")
    audit.save_request(request)

    persisted = audit.get_request(request.request_id)
    events = audit.list_events(request.request_id)

    assert persisted is not None
    assert persisted["opportunity_id"] == "OPP-001"
    assert persisted["status"] == "APPROVED"
    assert [event["to_status"] for event in events] == [
        "ELIGIBLE", "VALIDATED", "READY_FOR_REVIEW", "APPROVED"
    ]
    assert events[-1]["actor"] == "manager@example.com"
