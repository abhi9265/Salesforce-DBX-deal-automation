from adapters.databricks.registration import DatabricksRegistrationAdapter
from audit.processed_deals import SQLiteProcessedDealStore
from domain.models import Deal, RegistrationRequest
from domain.states import RegistrationStatus
from services.registration_processor import RegistrationProcessor
from services.mapping import map_to_dbx_draft


def test_registration_processor_submits_once_to_dbx_adapter(tmp_path):
    deal = Deal(
        opportunity_id="OPP-DBX-001",
        account_name="Acme",
        opportunity_name="Acme Platform",
        country="India",
        amount=125000,
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

    payload = map_to_dbx_draft({
        "account_name": deal.account_name,
        "opportunity_name": deal.opportunity_name,
        "country": deal.country,
        "amount": deal.amount,
        "industry": deal.industry,
        "partner": deal.partner,
        "close_date": deal.close_date,
    })

    processor = RegistrationProcessor(
        SQLiteProcessedDealStore(tmp_path / "idempotency.db"),
        DatabricksRegistrationAdapter(),
    )

    first = processor.process(deal, request, payload)
    second = processor.process(deal, request, payload)

    assert first.processed is True
    assert first.request.status == RegistrationStatus.REGISTERED
    assert second.processed is False
    assert second.skipped is True
    assert first.reason is None
