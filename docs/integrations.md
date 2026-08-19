# External integration architecture

## Salesforce

`SalesforceRestClient` owns HTTP transport, authentication headers, timeout behavior and bounded retry handling for transient responses. `SalesforceOpportunityAdapter` converts Salesforce records into the canonical `Deal` domain model.

The rest of the workflow never imports Salesforce field names.

```text
Salesforce REST API
       |
       v
SalesforceRestClient
       |
       v
SalesforceOpportunityAdapter
       |
       v
Canonical Deal
```

## Databricks registration

`DatabricksRegistrationHttpAdapter` is a configurable downstream boundary. It uses an idempotency key derived from the registration request UUID and distinguishes retryable transport/server responses from non-retryable rejection.

The endpoint and payload remain configuration-driven because the authorized downstream registration interface has not yet been supplied.

```text
RegistrationRequest
       |
       v
DBX mapping
       |
       v
HTTP adapter
       |
       v
Authorized downstream API
```

## Security

Credentials are loaded from environment variables and are never stored in source control. Production deployments should use a managed secret store and workload identity rather than long-lived developer tokens.
