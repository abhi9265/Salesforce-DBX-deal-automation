from __future__ import annotations

from uuid import uuid4


def test_request_identity_is_uuid():
    request_id = uuid4()
    assert len(str(request_id)) == 36
    assert request_id.version == 4
