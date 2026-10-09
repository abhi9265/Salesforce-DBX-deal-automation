from unittest.mock import Mock
from uuid import uuid4

import pytest
import requests

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


def test_dbx_http_adapter_classifies_timeout_as_unknown():
    session = Mock()
    session.post.side_effect = requests.Timeout("socket timed out")

    result = DatabricksRegistrationHttpAdapter(
        DatabricksRegistrationConfig("https://dbx.example/register", "token"),
        session=session,
    ).submit({}, uuid4())

    assert result.accepted is False
    assert result.unknown is True
    assert "unknown" in result.message.lower()


def test_dbx_http_adapter_classifies_malformed_success_as_unknown():
    session = Mock()
    session.post.return_value = Mock(status_code=201, content=b"not-json")
    session.post.return_value.json.side_effect = ValueError("invalid json")

    result = DatabricksRegistrationHttpAdapter(
        DatabricksRegistrationConfig("https://dbx.example/register", "token"),
        session=session,
    ).submit({}, uuid4())

    assert result.accepted is False
    assert result.unknown is True
    assert "malformed json" in result.message.lower()


def test_dbx_http_adapter_classifies_missing_registration_number_as_unknown():
    session = Mock()
    response = Mock(status_code=201, content=b'{"message":"accepted"}')
    response.json.return_value = {"message": "accepted"}
    session.post.return_value = response

    result = DatabricksRegistrationHttpAdapter(
        DatabricksRegistrationConfig("https://dbx.example/register", "token"),
        session=session,
    ).submit({}, uuid4())

    assert result.accepted is False
    assert result.unknown is True
    assert "registration number" in result.message.lower()


@pytest.mark.parametrize(
    ("body", "content"),
    [
        (None, b"null"),
        (["DBX-100"], b'["DBX-100"]'),
        ("DBX-100", b'"DBX-100"'),
        (42, b"42"),
    ],
)
def test_dbx_http_adapter_classifies_non_object_success_body_as_unknown(body, content):
    session = Mock()
    response = Mock(status_code=201, content=content)
    response.json.return_value = body
    session.post.return_value = response

    result = DatabricksRegistrationHttpAdapter(
        DatabricksRegistrationConfig("https://dbx.example/register", "token"),
        session=session,
    ).submit({}, uuid4())

    assert result.accepted is False
    assert result.unknown is True
    assert "non-object json body" in result.message.lower()


class _RegistrationHandler(__import__("http.server").server.BaseHTTPRequestHandler):
    seen_idempotency_keys = []

    def do_POST(self):
        self.__class__.seen_idempotency_keys.append(self.headers["Idempotency-Key"])
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"registration_number":"DBX-LIVE-TEST"}')

    def log_message(self, *_args):
        return


def test_dbx_http_adapter_works_against_local_http_boundary():
    from http.server import ThreadingHTTPServer
    from threading import Thread

    server = ThreadingHTTPServer(("127.0.0.1", 0), _RegistrationHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request_id = uuid4()
        result = DatabricksRegistrationHttpAdapter(
            DatabricksRegistrationConfig(
                f"http://127.0.0.1:{server.server_port}/register", "test-token"
            ),
        ).submit({"deal_name": "Acme"}, request_id)

        assert result.accepted is True
        assert result.registration_number == "DBX-LIVE-TEST"
        assert _RegistrationHandler.seen_idempotency_keys[-1] == str(request_id)
    finally:
        server.shutdown()
        server.server_close()
