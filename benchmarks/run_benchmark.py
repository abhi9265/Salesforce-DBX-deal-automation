"""Run a reproducible workflow benchmark with synthetic Salesforce-shaped deals."""
from __future__ import annotations

import csv
import json
import os
import tempfile
import time
from pathlib import Path

from audit.repository import AuditRepository
from domain.models import Deal
from services.workflow import DealRegistrationWorkflow


DEALS = int(os.getenv("BENCHMARK_DEALS", "1000"))
OUT = Path(os.getenv("BENCHMARK_OUT", "benchmark-results"))


def make_deal(i: int) -> Deal:
    return Deal(
        opportunity_id=f"OPP-{i:06d}",
        account_name=f"Account {i % 100:03d}",
        opportunity_name=f"Deal {i:06d}",
        country="US",
        amount=10000.0 + i,
        industry="Technology",
        partner="Partner A",
        close_date="2026-12-31",
        registration_required=True,
        registration_status="Open",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        audit = AuditRepository(Path(temp_dir) / "benchmark.db")
        workflow = DealRegistrationWorkflow(audit)
        start = time.perf_counter()
        registered = 0
        for i in range(DEALS):
            request = workflow.evaluate(make_deal(i))
            if request.status.value == "VALIDATED":
                workflow.prepare_for_review(request)
                workflow.approve(request, "benchmark-user")
                audit.save_request(request)
                registered += 1
        elapsed = time.perf_counter() - start
        result = {
            "workload_deals": DEALS,
            "workflow_evaluated": DEALS,
            "approved_requests": registered,
            "runtime_seconds": round(elapsed, 3),
            "deals_per_second": round(DEALS / elapsed, 2),
        }
        (OUT / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        with (OUT / "results.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=result.keys())
            writer.writeheader()
            writer.writerow(result)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
