from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

import requests

from adapters.databricks.registration import RegistrationResult
from config.integrations import DatabricksRegistrationConfig


class DatabricksRegistrationHttpAdapter:
    """Configurable downstream HTTP boundary for DBX registration."""

    def __init__(
        self,
        config: DatabricksRegistrationConfig,
        session: requests.Session | None = None,
    ) -> None:
        self.config = config
        self.session = session or requests.Session()

    def submit(
        self,
        payload: Mapping[str, Any],
        request_id: UUID,
    ) -> RegistrationResult:
        response = self.session.post(
            self.config.endpoint,
            headers={
                "Authorization": f"Bearer {self.config.token}",
                "Content-Type": "application/json",
                "Idempotency-Key": str(request_id),
            },
            json=dict(payload),
            timeout=self.config.timeout_seconds,
        )
        if 200 <= response.status_code < 300:
            body = response.json() if response.content else {}
            return RegistrationResult(
                accepted=True,
                registration_number=body.get("registration_number"),
                message=body.get("message"),
            )
        if response.status_code in {408, 429, 500, 502, 503, 504}:
            return RegistrationResult(
                False,
                message="Downstream DBX registration is retryable",
            )
        return RegistrationResult(
            False,
            message=(
                "Downstream DBX registration rejected: "
                f"HTTP {response.status_code}"
            ),
        )
