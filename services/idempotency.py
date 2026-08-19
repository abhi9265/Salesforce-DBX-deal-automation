from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def canonical_deal_hash(deal: Mapping[str, Any]) -> str:
    """Stable fingerprint used to skip unchanged opportunities."""
    payload = json.dumps(dict(deal), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
