# External Registration API Contract

This document defines the HTTP boundary expected by the Databricks registration adapter.

The repository does **not** claim that a production endpoint matching this contract exists. The contract is intentionally explicit so a real downstream team can be integrated without changing the workflow/domain layer.

## Request

**Method:** `POST`

**Content-Type:** `application/json`

Headers:

- `Authorization: Bearer <token>`
- `Idempotency-Key: <registration-request-uuid>`

Example payload:

```json
{
  "customer_name": "Acme",
  "deal_name": "Platform",
  "country": "India",
  "deal_amount": 100000,
  "industry": "Technology",
  "partner_name": "Databricks",
  "expected_close_date": "2026-09-30"
}
```

## Success

A `2xx` response must contain a confirmed registration identifier when the downstream operation is complete:

```json
{
  "registration_number": "DBX-10042",
  "message": "Registration accepted"
}
```

The workflow only transitions to `REGISTERED` after this identifier is received.

## Failure semantics

| HTTP response | Workflow interpretation |
| --- | --- |
| 2xx + registration number | Accepted and confirmed |
| 408 / 429 / 5xx | Retryable failure |
| Connection timeout / connection error | Outcome unknown |
| Other 4xx | Rejected / non-retryable |

A transport timeout is **not** treated as rejection and is **not** treated as success. The request enters `SUBMISSION_UNKNOWN` and can be reconciled using the same idempotency key.

## Idempotency

The `Idempotency-Key` is the durable registration request UUID. Retries and reconciliation must reuse the same key so the downstream service can return the existing registration instead of creating a second one.

The client should never generate a new idempotency key merely because the first network attempt timed out.

## Security expectations

Production implementations should:

- store tokens outside source control;
- use TLS for the endpoint;
- grant the integration identity only the required registration permission;
- avoid logging authorization headers or tokens;
- redact sensitive payload fields in application logs;
- validate the downstream response before changing workflow state.

## Scope boundary

The HTTP adapter and tests prove the client-side contract and failure classification. They do not prove the existence, authentication model, availability, or SLA of a real Databricks registration service.
