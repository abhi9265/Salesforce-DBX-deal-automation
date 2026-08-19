# Salesforce–Databricks Deal Automation

A rules-driven deal registration workflow for evaluating Salesforce opportunities against Databricks registration requirements, validating readiness, mapping fields across system boundaries, managing human approval, and preserving an auditable lifecycle.

> **Current scope:** local MVP with a Salesforce-shaped CSV source and SQLite audit store. External Salesforce and Databricks integrations are intentionally isolated behind adapters and are not claimed as implemented yet.

## Problem

Deal-registration workflows often span CRM data, partner rules, manual review, external submission, and follow-up tracking. The goal of this project is to create a clear, testable workflow engine so that business rules are separated from source-system and destination-system integrations.

## Architecture

```text
Salesforce / Mock Source
          |
          v
    Source Adapter
          |
          v
   Canonical Deal Model
          |
          v
    Eligibility Engine
          |
     +----+----+
     |         |
 Eligible    Not Eligible
     |
     v
 Validation Engine
     |
 +---+---+
 |       |
Valid   Invalid
 |
 v
Field Mapping
 |
 v
Registration Request
 |
 v
Workflow State Machine
 |
 +------------------------------+
 |              |               |
Approve       Reject         Exception
 |
 v
Submission Adapter
 |
 +------------+-------------+
 |                          |
Manual Portal          Future API
 |
 v
Registration Result
 |
 v
Immutable Audit Events
```

## Core capabilities

- Source abstraction for Salesforce / local mock data
- Eligibility rules separated from data validation
- Configurable field mapping
- Strongly defined registration workflow states
- Explicit handling for unknown submission outcomes
- Immutable audit-event design
- Unit and integration-testable business logic
- CI validation through GitHub Actions
- Clear separation between implemented MVP behavior and future integrations

## Repository structure

```text
app.py                  Streamlit presentation layer
config/                 configurable business rules
domain/                 domain models, states, exceptions
services/               business services
adapters/               source and destination integration boundaries
audit/                  request state + immutable event history
data/                   synthetic local fixtures
ai/                     future AI-assisted policy/readiness capabilities
tests/                  unit and integration tests
docs/                   architecture, ADRs and workflow documentation
.github/workflows/      CI automation
```

## Current integration boundary

The local application uses synthetic opportunity data. The Salesforce adapter is the boundary where a real Salesforce Sandbox/API implementation can be introduced later. The Databricks adapter is similarly isolated so the core workflow does not depend on browser automation or undocumented external interfaces.

## Engineering principles

1. **Rules decide; AI may explain.** Deterministic eligibility and validation remain authoritative.
2. **Integrations stay at the edge.** Salesforce and Databricks details should not leak into domain logic.
3. **Unknown external outcomes are explicit.** Never mark a submission registered without confirmation.
4. **Audit history is immutable.** State changes are events, not overwritten history.
5. **Implemented vs planned is explicit.** Documentation never claims an integration that is only a design placeholder.

## Roadmap

- [x] Local deal workflow prototype
- [x] Eligibility, validation and mapping foundations
- [x] Registration lifecycle model
- [ ] Immutable audit event history
- [ ] Salesforce Sandbox adapter
- [ ] Databricks registration adapter based on confirmed interface/contract
- [ ] Authentication and role-based approval
- [ ] Workflow metrics and operational SLAs
- [ ] AI-assisted policy extraction and readiness explanation

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

## Data safety

Only synthetic/sample data belongs in this repository. Do not commit Salesforce credentials, security tokens, access tokens, production exports, or real customer/deal information.
