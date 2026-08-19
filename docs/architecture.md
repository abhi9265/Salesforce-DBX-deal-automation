# Architecture

## Goal

Provide a maintainable decision and workflow engine for Databricks deal registration while keeping external-system integrations at the boundaries.

## Request lifecycle

```text
Source record
   ↓
Canonical deal
   ↓
Eligibility
   ↓
Validation
   ↓
Field mapping
   ↓
Registration request
   ↓
State machine
   ↓
Approval
   ↓
Submission adapter
   ↓
Confirmed registration / explicit unknown outcome
   ↓
Immutable audit event
```

## Boundaries

### Source adapter
Responsible for obtaining opportunity records. The current implementation can use synthetic local data. A Salesforce Sandbox implementation belongs behind the same boundary.

### Domain layer
Contains business meaning: deal model, lifecycle states and domain exceptions. It must not depend on Streamlit, Salesforce SDKs or Databricks-specific clients.

### Service layer
Eligibility, validation and mapping rules operate on canonical domain data.

### Destination adapter
Responsible for the external registration mechanism. The project must not automate a third-party portal through browser scraping unless an approved interface exists.

### Audit layer
Stores the current request state separately from immutable transition events so operational state and historical evidence are both available.

## Security boundary

Credentials belong only in environment/secret stores. Source exports and real customer/deal records must never be committed to GitHub.

## AI boundary

Deterministic business rules remain authoritative. AI may later extract policy requirements or explain why a deal is blocked, but it must not silently change eligibility or validation rules.
