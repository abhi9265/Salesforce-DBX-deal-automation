from domain.models import Deal
from audit.repository_complete import AuditRepositoryComplete
from services.workflow import DealRegistrationWorkflow
from services.mapping import map_to_dbx_draft
from adapters.databricks.registration import DatabricksRegistrationAdapter


def test_end_to_end_ready_for_external_registration(tmp_path):
    audit = AuditRepositoryComplete(tmp_path / "audit.db")
    workflow = DealRegistrationWorkflow(audit)
    deal = Deal(
        opportunity_id="OPP-E2E-001", account_name="Acme Corp",
        opportunity_name="Lakehouse Modernization", country="India",
        amount=250000.0, industry="Technology", partner="Databricks",
        close_date="2026-12-31", registration_required=True,
        registration_status="Not Registered",
    )
    request = workflow.evaluate(deal)
    assert request.status.value == "VALIDATED"
    workflow.prepare_for_review(request)
    workflow.approve(request, "manager@example.com")
    audit.save_request(request)

    payload = map_to_dbx_draft({
        "account_name": deal.account_name,
        "opportunity_name": deal.opportunity_name,
        "country": deal.country,
        "amount": deal.amount,
        "industry": deal.industry,
        "partner": deal.partner,
        "close_date": deal.close_date,
    })
    result = DatabricksRegistrationAdapter().submit(payload, request.request_id)
    assert result.accepted
    assert result.registration_number.startswith("DBX-")
