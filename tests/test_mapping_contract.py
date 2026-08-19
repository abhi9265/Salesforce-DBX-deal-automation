from services.mapping import map_source_record, map_to_dbx_draft


def test_salesforce_mapping_normalizes_source_fields():
    result = map_source_record({
        "Opportunity_ID": "OPP-1",
        "Account_Name": "Acme",
        "Amount": "125000",
    })
    assert result == {"opportunity_id": "OPP-1", "account_name": "Acme", "amount": "125000"}


def test_dbx_mapping_is_explicit_draft_contract():
    result = map_to_dbx_draft({
        "account_name": "Acme",
        "opportunity_name": "Platform",
        "amount": 125000,
    })
    assert result["customer_name"] == "Acme"
    assert result["deal_name"] == "Platform"
    assert result["deal_amount"] == 125000
