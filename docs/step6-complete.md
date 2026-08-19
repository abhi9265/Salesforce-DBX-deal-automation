# Step 6 completion

Step 6 completes the local registration submission lifecycle:

- successful downstream submission moves `APPROVED -> SUBMITTED -> REGISTERED` when a registration number is returned;
- failed submission moves `APPROVED -> SUBMISSION_FAILED`;
- submission transitions can be persisted to the audit history;
- successful processing is recorded in the durable idempotency store only after downstream acceptance;
- lifecycle behavior is covered by integration-style tests.

The external Salesforce and Databricks systems remain adapter boundaries. This repository does not claim production credentials or a live downstream contract.
