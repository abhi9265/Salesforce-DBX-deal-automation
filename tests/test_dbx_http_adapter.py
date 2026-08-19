from unittest.mock import Mock
from uuid import uuid4

from adapters.databricks.http_registration import DatabricksRegistrationHttpAdapter
from config.integrations import DatabricksRegistrationConfig


def test_dbx_http_adapter_sends_idempotency_key():
    session = Mock()
    response = Mock(status_code=201, content=b'{"registration_number":"DBX-100"}')
    response.json.return_value = {"registration_number": "DBX-100"}
    session.post.return_value = response
    request_id = uuid4()

    result = DatabricksRegistrationHttpAdapter(
        DatabricksRegistrationConfig("https://dbx.example/register", "token"),
        session=session,
    ).submit({"deal_name": "Acme"}, request_id)

    assert result.accepted is True
    assert result.registration_number == "DBX-100"
    assert session.post.call_args.kwargs["headers"]["Idempotency-Key"] == str(request_id)


def test_dbx_http_adapter_classifies_retryable_failure():
    session = Mock()
    session.post.return_value = Mock(status_code=503, content=b"")

    result = DatabricksRegistrationHttpAdapter(
        DatabricksRegistrationConfig("https://dbx.example/register", "token"),
        session=session,
    ).submit({}, uuid4())

    assert result.accepted is False
    assert "retryable" in result.message.lower()
