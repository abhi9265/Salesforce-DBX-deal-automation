"""Measure the repository's executable workflow verification suite."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import time
from pathlib import Path

OUT = Path(os.getenv("BENCHMARK_OUT", "benchmark-results"))
TARGET = os.getenv("BENCHMARK_TARGET", "tests")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    completed = subprocess.run(
        ["python", "-m", "pytest", TARGET, "-q"],
        text=True,
        capture_output=True,
    )
    elapsed = time.perf_counter() - start
    if completed.returncode:
        print(completed.stdout)
        print(completed.stderr)
        raise SystemExit(completed.returncode)
    result = {
        "benchmark_type": "executable_workflow_test_suite",
        "target": TARGET,
        "runtime_seconds": round(elapsed, 3),
        "status": "passed",
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (OUT / "results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=result.keys())
        writer.writeheader()
        writer.writerow(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
