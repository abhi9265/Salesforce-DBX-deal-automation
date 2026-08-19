# Step 6 report

Step 6 adds the submission lifecycle and audit integration on top of the current `main` architecture.

## Lifecycle

`APPROVED -> SUBMITTED -> REGISTERED` when the downstream adapter returns a registration number.

`APPROVED -> SUBMISSION_FAILED` when the downstream adapter rejects the request.

`SUBMISSION_UNKNOWN` remains available for accepted-but-unconfirmed outcomes.

## Reliability

Successful processing is recorded in the durable processed-deal store only after downstream acceptance. Re-delivery of an unchanged source version remains idempotent.

## Audit

Submission transitions can be recorded with request ID, opportunity ID, previous status, new status, reason and event timestamp.

## Testing

Step 6 includes lifecycle/audit integration coverage and a smoke test. CI must be allowed to execute before the branch is called green or merged.

## Scope boundary

This is still a local MVP. Salesforce and Databricks remain integration boundaries; no production credentials or undocumented external contract is claimed.
