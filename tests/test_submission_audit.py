from adapters.databricks.registration import DatabricksRegistrationAdapter
from audit.processed_deals import SQLiteProcessedDealStore
from audit.repository import AuditRepository
from domain.models import Deal, RegistrationRequest
from domain.states import RegistrationStatus
from services.mapping import map_to_dbx_draft
from services.registration_processor import RegistrationProcessor


def test_successful_submission_is_audited(tmp_path):
    deal = Deal(
        opportunity_id="OPP-AUDIT-001", account_name="Acme", opportunity_name="Platform",
        country="India", amount=100000, industry="Technology", partner="Databricks",
        close_date="2026-09-30", registration_required=True,
        registration_status="Not Registered",
    )
    request = RegistrationRequest(deal.opportunity_id)
    request.transition(RegistrationStatus.ELIGIBLE)
    request.transition(RegistrationStatus.VALIDATED)
    request.transition(RegistrationStatus.READY_FOR_REVIEW)
    request.approve("manager@example.com")

    audit = AuditRepository(tmp_path / "audit.db")
    processor = RegistrationProcessor(
        SQLiteProcessedDealStore(tmp_path / "idempotency.db"),
        DatabricksRegistrationAdapter(),
        audit=audit,
    )

    processor.process(
        deal,
        request,
        map_to_dbx_draft({"account_name": deal.account_name, "opportunity_name": deal.opportunity_name}),
    )

    history = audit.history(request.request_id)
    assert [event["to_status"] for event in history] == ["SUBMITTED", "REGISTERED"]
