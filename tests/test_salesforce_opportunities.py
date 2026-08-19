from unittest.mock import Mock

from adapters.salesforce.opportunities import SalesforceOpportunityAdapter


def test_salesforce_opportunity_is_normalized_to_domain_deal():
    client = Mock()
    client.query.return_value = [{
        "Id": "006001",
        "Account": {"Name": "Acme"},
        "Name": "Acme Data Platform",
        "Country__c": "India",
        "Amount": 150000,
        "Industry": "Technology",
        "Partner__c": "Databricks",
        "CloseDate": "2026-10-15",
        "Registration_Required__c": True,
        "Registration_Status__c": "Not Registered",
    }]

    deals = SalesforceOpportunityAdapter(client).fetch_opportunities()
    assert len(deals) == 1
    assert deals[0].opportunity_id == "006001"
    assert deals[0].account_name == "Acme"
    assert deals[0].amount == 150000
    assert deals[0].registration_required is True
