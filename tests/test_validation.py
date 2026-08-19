from services.validation import validate_deal


def test_valid_deal_has_no_validation_errors():
    deal = {
        "account_name": "ABC Corp",
        "opportunity_name": "ABC Migration",
        "country": "USA",
        "amount": "250000",
        "industry": "Financial Services",
        "partner": "Databricks",
        "close_date": "2026-09-30",
    }
    assert validate_deal(deal) == []


def test_invalid_amount_and_date_are_reported():
    deal = {
        "account_name": "ABC Corp",
        "opportunity_name": "ABC Migration",
        "country": "USA",
        "amount": "not-a-number",
        "industry": "Financial Services",
        "partner": "Databricks",
        "close_date": "30-09-2026",
    }
    errors = validate_deal(deal)
    assert any("amount" in error.lower() for error in errors)
    assert any("close_date" in error.lower() for error in errors)
