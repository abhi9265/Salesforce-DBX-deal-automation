from __future__ import annotations

import time
from typing import Any, Callable, Mapping

import requests

from config.integrations import SalesforceConfig


class SalesforceApiError(RuntimeError):
    pass


class SalesforceRestClient:
    """Thin REST transport. Business mapping stays outside this class."""

    def __init__(
        self,
        config: SalesforceConfig,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self.session = session or requests.Session()
        self.sleep = sleep

    def query(self, soql: str, *, max_attempts: int = 3) -> list[Mapping[str, Any]]:
        url = f"{self.config.base_url}/services/data/{self.config.api_version}/query"
        headers = {"Authorization": f"Bearer {self.config.access_token}"}
        params = {"q": soql}

        for attempt in range(max_attempts):
            response = self.session.get(url, headers=headers, params=params, timeout=20)
            if response.ok:
                payload = response.json()
                return payload.get("records", [])
            if response.status_code in {429, 500, 502, 503, 504} and attempt < max_attempts - 1:
                self.sleep(2**attempt)
                continue
            raise SalesforceApiError(
                f"Salesforce query failed: HTTP {response.status_code}"
            )
        raise SalesforceApiError("Salesforce query failed after retries")
