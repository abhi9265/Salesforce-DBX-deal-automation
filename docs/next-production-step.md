# Next production step

The local MVP now has the core persistence and workflow boundaries needed for a production-shaped implementation.

The next implementation should replace the mock adapters only when the authorized Salesforce and Databricks interfaces are available.

Production path:

```text
Salesforce API / CDC
        ↓
Salesforce adapter
        ↓
Canonical Deal
        ↓
Eligibility + validation
        ↓
Registration request + audit events
        ↓
Authorized Databricks registration API
        ↓
Registration result
```

No credentials, customer data, or undocumented external API behavior should be added to the repository.
