from pathlib import Path

from adapters.salesforce.mock_salesforce import MockSalesforceAdapter
from audit.repository import AuditRepository
from domain.states import RegistrationStatus
from services.eligibility import is_eligible
from services.workflow import DealRegistrationWorkflow


FIXTURE = Path("data/sample_opportunities.csv")


def test_mock_salesforce_fixture_loads_expected_deals():
    deals = MockSalesforceAdapter(FIXTURE).list_opportunities()
    assert len(deals) == 25
    assert deals[0].opportunity_id == "OPP-1001"
    assert deals[0].source_system == "salesforce-mock"


def test_eligible_deal_moves_to_validated_and_audits(tmp_path):
    deal = MockSalesforceAdapter(FIXTURE).list_opportunities()[0]
    assert is_eligible(deal)

    audit = AuditRepository(tmp_path / "audit.db")
    workflow = DealRegistrationWorkflow(audit)
    request = workflow.evaluate(deal)

    assert request.status == RegistrationStatus.VALIDATED
    workflow.prepare_for_review(request)
    workflow.approve(request, "manager@example.com")

    history = audit.history(request.request_id)
    assert [event["to_status"] for event in history] == [
        "ELIGIBLE",
        "VALIDATED",
        "READY_FOR_REVIEW",
        "APPROVED",
    ]


def test_invalid_deal_is_not_approved(tmp_path):
    deal = MockSalesforceAdapter(FIXTURE).list_opportunities()[6]
    audit = AuditRepository(tmp_path / "audit.db")
    workflow = DealRegistrationWorkflow(audit)
    request = workflow.evaluate(deal)

    assert request.status == RegistrationStatus.VALIDATION_FAILED
    assert request.validation_errors
