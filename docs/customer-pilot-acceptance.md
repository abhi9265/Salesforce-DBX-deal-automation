# Customer pilot: discovery, acceptance and handoff

This checklist is for taking the local deal-registration MVP through a customer-facing discovery and pilot conversation. It is deliberately not a production deployment guide: the Salesforce and Databricks adapters still need the customer's authorized interfaces and environment details.

## 1. Start with the workflow outcome

Before wiring APIs, agree with the customer on:

- Which opportunity types are in scope, and which must be excluded.
- Who owns eligibility rules, required fields and approval decisions.
- What business event means a registration is truly complete.
- What duplicate registration would cost, and who can resolve an ambiguous submission.
- How success will be measured during a pilot (for example, fewer manual handoffs, lower review time, or fewer incomplete submissions). Capture a baseline before claiming improvement.

Do not start implementation until a business owner and an operational owner are named.

## 2. Integration discovery

| Area | Questions to resolve with the customer | Evidence required before implementation |
|---|---|---|
| Salesforce source | REST API or CDC? Which object and fields? What permissions and API limits apply? | Approved field list, sample records with sensitive values removed, auth method and rate-limit guidance |
| Incremental sync | Which timestamp/version is authoritative? How are deletes and late updates represented? | Agreed watermark, overlap/replay strategy and delete semantics |
| Data contract | Which fields are required, nullable, enumerated or normalized? Which currency and date conventions apply? | Signed-off mapping and representative valid/invalid examples |
| Approval | Who approves, rejects or reopens a request? Is approval tied to a specific source version? | Named roles and state-transition rules |
| Downstream registration | What endpoint, auth, idempotency and response contract are supported? | Approved API specification and sandbox access from the service owner |
| Operations | Who receives failures? What response time and retry policy are acceptable? | Support owner, alert route, retry/reconciliation policy and escalation path |
| Security | Which data may be persisted/logged? What retention and access rules apply? | Data classification, retention decision and approved secret-management approach |

Do not guess an external API schema or use production credentials in the repository. The current Databricks registration contract is a draft until the downstream service owner confirms it.

## 3. Pilot acceptance gates

Use a customer-approved test dataset and record the result of each gate. A gate is not passed merely because the local mock succeeds.

| Gate | Acceptance condition | Current evidence boundary |
|---|---|---|
| Mapping | Agreed source fields map to the canonical `Deal` model without silent data loss | Local mapping tests; customer mapping approval still required |
| Validation | Missing/invalid required fields produce actionable validation failures | Covered by local rules/tests; customer rules must be signed off |
| Approval | Submission cannot proceed before the authorized approval state | Local workflow tests; customer identity/role integration is not established |
| Duplicate protection | Replayed request uses the same request identity/idempotency key and does not create a second registration | Local idempotency tests; downstream enforcement must be verified with the real API |
| Ambiguous outcome | Timeout or malformed/unconfirmed response remains unresolved, not falsely marked registered | Adapter tests; real service behavior remains unverified |
| Reconciliation | Operator can identify unresolved submissions and reconcile them with the downstream owner | Define and test the customer-specific operating procedure before go-live |
| Audit | Request state and lifecycle events let an operator explain what happened without exposing secrets | Local persistence/audit tests; customer retention/access requirements remain open |
| Recovery | A controlled retry/replay recovers from a transient failure without duplicating side effects | Demonstrate in an authorized sandbox before production approval |

## 4. Suggested pilot walkthrough

1. Load a small, customer-approved set of representative opportunities, including invalid and duplicate cases.
2. Compare the canonical records with the source and have the business owner sign off on the mapping.
3. Run eligibility and validation; review rejected records with the business owner.
4. Complete the approval step with the intended operational roles.
5. Exercise accepted, rejected, timed-out and malformed downstream responses in a sandbox or controlled test double.
6. Re-run the same request to verify idempotency and confirm the outcome is reconciled rather than guessed.
7. Review the audit trail with the operator who would handle a real incident.
8. Record defects, owners and acceptance decisions. Do not proceed to production while the downstream contract, access controls, reconciliation procedure or support ownership is unresolved.

## 5. Handoff checklist

Before calling a pilot ready for handoff, capture:

- [ ] Business owner and operational/support owner
- [ ] Approved source-to-canonical mapping and eligibility rules
- [ ] Confirmed downstream API contract, auth and idempotency semantics
- [ ] Agreed retry, unknown-outcome and manual reconciliation procedure
- [ ] Secret storage, least-privilege access, data retention and log-redaction decisions
- [ ] Customer-approved acceptance results, defects and sign-off
- [ ] Rollback/disable procedure and escalation contacts
- [ ] Baseline and measured pilot outcomes, with the measurement window recorded

## Current scope boundary

This repository demonstrates the workflow with synthetic Salesforce-shaped data, local persistence, a mock adapter and automated tests. These checks help validate application behavior, but they do not establish a live Salesforce connection, a real Databricks registration service, customer acceptance, production deployment or business impact. Those claims require evidence from the customer's authorized environment.
