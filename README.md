# Salesforce–Databricks Deal Automation

A small, rules-driven workflow engine for automating Salesforce opportunity → Databricks deal registration.

> **Current scope:** local MVP using synthetic Salesforce-shaped data, SQLite persistence, a deterministic workflow engine, and a mock Databricks registration adapter. Real Salesforce/Databricks credentials and external contracts are intentionally not committed or claimed.

## Problem

Deal registration can require CRM data extraction, eligibility rules, validation, human approval, downstream submission, retries, and auditability. This project keeps those responsibilities explicit and testable instead of coupling business rules to Salesforce or Databricks implementation details.

## Architecture

```text
Salesforce / Mock Source
          |
          v
    Salesforce Adapter
          |
          v
     Canonical Deal
          |
          v
 Eligibility + Validation
          |
          v
 Registration Request
          |
          v
 Approval State Machine
          |
          v
  Salesforce → DBX Mapping
          |
          v
 Databricks Registration Adapter
          |
          v
 Registration Result
          |
          +-------------------+
          |                   |
          v                   v
   Durable Idempotency     Audit History
```

The core lifecycle is deterministic:

```text
NEW
 ↓
ELIGIBLE
 ↓
VALIDATED
 ↓
READY_FOR_REVIEW
 ↓
APPROVED
 ↓
SUBMITTED
 ↓
REGISTERED
```

Exception states such as `NOT_ELIGIBLE`, `VALIDATION_FAILED`, `SUBMISSION_FAILED`, and `SUBMISSION_UNKNOWN` are explicit.

## Implemented capabilities

- Salesforce-shaped mock adapter with CSV fixtures
- Incremental processing contract using source update timestamps
- Successful-sync watermark semantics
- Canonical `Deal` domain model
- Deterministic eligibility and validation
- Explicit field mapping across system boundaries
- Strict registration state transitions
- Human approval workflow
- UUID-based registration request identity
- Durable SQLite request/audit persistence
- Immutable registration event history
- Deterministic deal fingerprinting
- Durable idempotency store
- Mock Databricks registration adapter
- Retry/timeout boundaries for the real external adapters
- GitHub Actions CI with automated pytest execution
- Unit and integration tests covering the workflow and external boundaries

## Repository structure

```text
app.py                  Streamlit presentation layer
config/                 configuration and business rules
domain/                 domain models, states and exceptions
services/               workflow, validation, mapping and processing
adapters/               Salesforce and Databricks integration boundaries
audit/                  request, event and idempotency persistence
data/                   synthetic local fixtures
tests/                  unit and integration tests
docs/                   architecture and workflow documentation
.github/workflows/      CI automation
```

## External integration boundary

The repository intentionally separates the local MVP from real external connectivity:

```text
Current
CSV → Salesforce adapter → workflow → mock DBX adapter → SQLite audit

Target
Salesforce Sandbox/API → workflow → authorized Databricks interface
```

The real downstream contract should be introduced only after its authorized schema/API is confirmed.

## Engineering principles

1. **Rules decide; AI may explain.** Deterministic business rules remain authoritative.
2. **Integrations stay at the edge.** Salesforce and Databricks details do not leak into domain logic.
3. **Idempotency is explicit.** Re-delivery of the same business version must not create duplicate registrations.
4. **Unknown outcomes are explicit.** A request is not marked registered without confirmation.
5. **Audit history is immutable.** State transitions are recorded as events.
6. **Simple architecture wins.** No Bronze/Silver/Gold or extra platform components are introduced unless the business requirement actually needs them.
7. **Implemented vs planned is explicit.** Documentation does not claim a production integration that is only a mock or design boundary.

## Roadmap

- [x] Local workflow MVP
- [x] Eligibility, validation and mapping
- [x] Approval state machine
- [x] Incremental processing contract
- [x] Durable request and audit persistence
- [x] Durable idempotency
- [x] Mock DBX registration adapter
- [x] CI + automated tests
- [ ] Salesforce Sandbox/API implementation
- [ ] Confirmed Databricks registration contract
- [ ] Authentication and role-based approval
- [ ] Operational metrics and SLAs
- [ ] AI-assisted policy extraction and grounded readiness explanations

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[test]'
pytest
streamlit run app.py
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

## Data safety

Only synthetic/sample data belongs in this repository. Never commit Salesforce credentials, security tokens, access tokens, production exports, or real customer/deal information.
