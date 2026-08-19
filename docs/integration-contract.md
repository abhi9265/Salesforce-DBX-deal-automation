# Integration contract

## Salesforce source

The application consumes a canonical `Deal` model. Salesforce field names remain isolated to the source adapter and mapping layer.

## Databricks registration

The downstream payload currently remains a **draft contract** because the real Databricks registration API/schema has not been supplied.

Required draft fields:

- `customer_name`
- `deal_name`
- `country`
- `deal_amount`
- `industry`
- `partner_name`
- `expected_close_date`

The mock adapter validates the minimum contract and returns a deterministic registration identifier for local testing. It must not be described as a production Databricks API integration.
