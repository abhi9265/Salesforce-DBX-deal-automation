from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def canonical_deal_hash(deal: Mapping[str, Any]) -> str:
    """Stable fingerprint used to skip unchanged opportunities."""
    payload = json.dumps(dict(deal), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def deal_fingerprint(deal: Any) -> str:
    """Fingerprint the business fields that can change registration behavior."""
    payload = {
        "opportunity_id": deal.opportunity_id,
        "account_name": deal.account_name,
        "opportunity_name": deal.opportunity_name,
        "country": deal.country,
        "amount": deal.amount,
        "industry": deal.industry,
        "partner": deal.partner,
        "close_date": deal.close_date,
        "registration_required": deal.registration_required,
        "registration_status": deal.registration_status,
    }
    return canonical_deal_hash(payload)


class ProcessedDealStore:
    """Minimal persistence interface for successfully processed source versions."""

    def has_processed(self, opportunity_id: str, fingerprint: str) -> bool:
        raise NotImplementedError

    def mark_processed(self, opportunity_id: str, fingerprint: str) -> None:
        raise NotImplementedError
