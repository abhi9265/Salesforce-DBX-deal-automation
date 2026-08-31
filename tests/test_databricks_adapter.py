from uuid import uuid4

from adapters.databricks.registration import DatabricksRegistrationAdapter


VALID_PAYLOAD = {
    "customer_name": "Acme",
    "deal_name": "Acme Platform",
    "country": "India",
    "deal_amount": 100000,
    "industry": "Technology",
    "partner_name": "Databricks",
    "expected_close_date": "2026-09-30",
}


def test_draft_databricks_adapter_returns_registration_number():
    result = DatabricksRegistrationAdapter().submit(VALID_PAYLOAD, uuid4())
    assert result.accepted is True
    assert result.registration_number.startswith("DBX-")


def test_draft_databricks_adapter_rejects_incomplete_payload():
    result = DatabricksRegistrationAdapter().submit(
        {"customer_name": "Acme"},
        uuid4(),
    )
    assert result.accepted is False
    assert result.registration_number is None
    assert "deal_name" in result.message
