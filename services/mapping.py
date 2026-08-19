from __future__ import annotations

from typing import Any, Mapping

# Canonical synthetic Salesforce fixture field names.
SALESFORCE_TO_INTERNAL = {
    "OpportunityId": "opportunity_id",
    "AccountName": "account_name",
    "OpportunityName": "opportunity_name",
    "Country": "country",
    "Amount": "amount",
    "Industry": "industry",
    "Partner": "partner",
    "CloseDate": "close_date",
    "RegistrationRequired": "registration_required",
    "RegistrationStatus": "registration_status",
}

# Draft DBX contract. This remains explicitly versioned as a proposal until
# the real downstream Databricks registration interface is confirmed.
INTERNAL_TO_DBX_DRAFT = {
    "account_name": "customer_name",
    "opportunity_name": "deal_name",
    "country": "country",
    "amount": "deal_amount",
    "industry": "industry",
    "partner": "partner_name",
    "close_date": "expected_close_date",
}


def map_source_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        internal: record.get(source)
        for source, internal in SALESFORCE_TO_INTERNAL.items()
        if source in record
    }


def map_to_dbx_draft(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        dbx: record.get(internal)
        for internal, dbx in INTERNAL_TO_DBX_DRAFT.items()
        if internal in record
    }
