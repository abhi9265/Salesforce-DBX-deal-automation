from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SalesforceConfig:
    base_url: str
    access_token: str
    api_version: str = "v60.0"

    @classmethod
    def from_env(cls) -> "SalesforceConfig":
        return cls(
            base_url=os.environ["SALESFORCE_BASE_URL"].rstrip("/"),
            access_token=os.environ["SALESFORCE_ACCESS_TOKEN"],
            api_version=os.getenv("SALESFORCE_API_VERSION", "v60.0"),
        )


@dataclass(frozen=True, slots=True)
class DatabricksRegistrationConfig:
    endpoint: str
    token: str
    timeout_seconds: float = 20.0

    @classmethod
    def from_env(cls) -> "DatabricksRegistrationConfig":
        return cls(
            endpoint=os.environ["DBX_REGISTRATION_ENDPOINT"],
            token=os.environ["DBX_REGISTRATION_TOKEN"],
            timeout_seconds=float(os.getenv("DBX_REGISTRATION_TIMEOUT", "20")),
        )
