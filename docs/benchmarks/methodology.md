# Benchmark Methodology

## Purpose

Measure the local workflow's reliability and throughput without presenting a mock downstream adapter as a production integration benchmark.

## Protocol

1. Fix Python and repository revision.
2. Generate a deterministic set of Salesforce-shaped opportunities.
3. Record input requests, successful registrations, validation failures, downstream failures, unknown outcomes, retries, and audit events.
4. Measure wall-clock processing time and request throughput.
5. Repeat each workload at least three times and report the median.
6. Store results with the commit SHA and execution environment.

## Reliability scenarios

At minimum, exercise duplicate delivery, replay of an already registered request, validation failure, downstream rejection, and unknown downstream outcome.

## Reporting rule

Do not commit estimated performance numbers. Benchmark results should only be added after an actual run.