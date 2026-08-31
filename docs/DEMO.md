# Local Workflow Demo

The local MVP demonstrates the complete business workflow with synthetic Salesforce-shaped data and a mock Databricks registration boundary.

## Run

```bash
python -m pip install -e '.[test]'
pytest
streamlit run app.py
```

## Workflow

```text
Salesforce fixture
      ↓
incremental sync
      ↓
canonical Deal
      ↓
eligibility + validation
      ↓
registration request
      ↓
human approval
      ↓
idempotency check
      ↓
field mapping
      ↓
mock Databricks registration
      ↓
REGISTERED / failure / unknown
      ↓
SQLite request state + audit events
```

The demo is intentionally local. Real Salesforce authentication and the production Databricks registration contract remain adapter boundaries until those external contracts are known.
