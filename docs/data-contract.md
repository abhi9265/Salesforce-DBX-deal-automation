# Salesforce → DBX Registration Contract

## Canonical deal

The workflow engine consumes a normalized `Deal` model. Source-specific Salesforce names are translated at the adapter boundary.

## Draft DBX payload

Until the downstream Databricks registration interface is confirmed, the repository uses a **draft contract**:

| Internal field | Draft DBX field |
|---|---|
| `account_name` | `customer_name` |
| `opportunity_name` | `deal_name` |
| `country` | `country` |
| `amount` | `deal_amount` |
| `industry` | `industry` |
| `partner` | `partner_name` |
| `close_date` | `expected_close_date` |

This mapping is intentionally not represented as a production API contract. The adapter must be replaced or configured when the authorized downstream schema/API is available.

## Design rule

The domain and workflow layers must not depend on Salesforce field names or Databricks API details. External contracts belong in adapters and mapping modules.
