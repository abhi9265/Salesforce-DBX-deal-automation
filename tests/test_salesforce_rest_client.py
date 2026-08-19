from unittest.mock import Mock

import pytest

from adapters.salesforce.rest_client import SalesforceApiError, SalesforceRestClient
from config.integrations import SalesforceConfig


def _config():
    return SalesforceConfig("https://example.my.salesforce.com", "token", "v60.0")


def test_salesforce_query_returns_records():
    session = Mock()
    response = Mock(ok=True)
    response.json.return_value = {"records": [{"Id": "OPP-1"}]}
    session.get.return_value = response

    client = SalesforceRestClient(_config(), session=session)
    assert client.query("SELECT Id FROM Opportunity") == [{"Id": "OPP-1"}]
    session.get.assert_called_once()


def test_salesforce_query_retries_transient_failure():
    session = Mock()
    failed = Mock(ok=False, status_code=503)
    success = Mock(ok=True)
    success.json.return_value = {"records": []}
    session.get.side_effect = [failed, success]

    client = SalesforceRestClient(_config(), session=session, sleep=lambda _: None)
    assert client.query("SELECT Id FROM Opportunity") == []
    assert session.get.call_count == 2


def test_salesforce_query_raises_for_non_retryable_failure():
    session = Mock()
    response = Mock(ok=False, status_code=401)
    session.get.return_value = response

    with pytest.raises(SalesforceApiError):
        SalesforceRestClient(_config(), session=session).query("SELECT Id FROM Opportunity")
