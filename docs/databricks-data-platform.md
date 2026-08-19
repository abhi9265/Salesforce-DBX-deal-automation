# Step 4 — Databricks data platform

This phase introduces the data-engineering boundary between Salesforce ingestion and the deal-registration workflow.

## Layers

```text
Salesforce / source adapter
        |
        v
Bronze Delta
  raw payload + source metadata
        |
        v
Silver Delta
  typed canonical opportunity
        |
        v
Gold Delta
  registration KPIs / business metrics
```

## Incremental strategy

The Bronze contract preserves a stable source identity, source modification timestamp, and pipeline run ID. Silver processing uses an idempotent `MERGE` keyed by opportunity ID and only updates a record when the source version is newer.

This avoids full-table recomputation for every Salesforce extraction.

## Operational controls

The platform includes contracts for:

- pipeline run auditing
- data-quality rule results
- record counts in/out/rejected
- watermark tracking
- failure messages
- environment-aware Unity Catalog objects

## Important implementation boundary

The repository contains **Databricks deployment/data-contract artifacts**, not a claim that a live Databricks workspace is connected to this public repository. Workspace paths, catalog names, credentials, and production endpoints remain deployment configuration.
