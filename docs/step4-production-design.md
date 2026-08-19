# Step 4 — production data-platform design

## Incremental processing

The platform uses a source modification version as the incremental boundary. A successful watermark is persisted only after the run completes its downstream controls. This prevents a failed run from advancing the cursor and silently losing source changes.

## SCD Type 2

`silver.opportunities_history` preserves business-key history using:

- `effective_from`
- `effective_to`
- `is_current`
- `record_hash`
- `source_updated_at`

A changed source version closes the current record and creates a new current version. Unchanged versions are ignored.

## Data-quality gates

Critical rules are persisted as first-class results. The initial rules cover:

1. opportunity ID completeness
2. non-negative deal amount
3. uniqueness of the current SCD2 version

The orchestration layer should fail the run when a critical rule returns `FAIL`.

## Audit and observability

Each run should expose:

- run ID
- environment
- source watermark
- input/output/rejected counts
- stage duration
- throughput
- quality status
- error message

This makes the pipeline diagnosable without inspecting executor logs manually.

## Performance strategy

The design intentionally avoids a full Silver rebuild. Optimization should be evidence-driven from stage telemetry. Candidate actions include pruning the incremental source window, minimizing columns carried from Bronze, and applying Delta maintenance only when observed table growth/query patterns justify it.

## Production boundary

The SQL is production-shaped and deployment-oriented, but this public repository does not claim a connected Databricks workspace. Real catalog names, credentials, secrets, cluster/serverless configuration, schedules, and Salesforce CDC credentials belong in deployment configuration.
