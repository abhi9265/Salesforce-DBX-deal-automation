from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from domain.policy import DEFAULT_POLICY, RegistrationPolicy


def _blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def validate_deal(deal: Mapping[str, Any], policy: RegistrationPolicy = DEFAULT_POLICY) -> list[str]:
    errors: list[str] = []

    for field in policy.required_fields:
        if _blank(deal.get(field)):
            errors.append(f"Missing: {field}")

    for field in policy.numeric_fields:
        value = deal.get(field)
        if _blank(value):
            continue
        try:
            if float(value) <= 0:
                errors.append(f"Invalid value: {field} must be greater than 0")
        except (TypeError, ValueError):
            errors.append(f"Invalid format: {field} must be numeric")

    for field in policy.date_fields:
        value = deal.get(field)
        if _blank(value):
            continue
        try:
            datetime.strptime(str(value).strip(), "%Y-%m-%d")
        except ValueError:
            errors.append(f"Invalid format: {field} must be YYYY-MM-DD")

    for field, allowed in policy.allowed_values.items():
        value = deal.get(field)
        if allowed and not _blank(value) and str(value).strip() not in allowed:
            errors.append(f"Invalid value: {field} must be one of {list(allowed)}")

    return errors
