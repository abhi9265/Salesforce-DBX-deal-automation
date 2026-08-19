from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class RegistrationPolicy:
    required_fields: tuple[str, ...]
    numeric_fields: tuple[str, ...]
    date_fields: tuple[str, ...]
    allowed_values: Mapping[str, tuple[str, ...]]
    partner: str = "Databricks"


DEFAULT_POLICY = RegistrationPolicy(
    required_fields=(
        "account_name",
        "opportunity_name",
        "country",
        "amount",
        "industry",
        "partner",
        "close_date",
    ),
    numeric_fields=("amount",),
    date_fields=("close_date",),
    allowed_values={"partner": ("Databricks",)},
)
