from __future__ import annotations

from typing import Any, Mapping

# Supported Salesforce source spellings are intentionally explicit so the
# adapter can normalize both API-style and synthetic fixture records.
SALESFORCE_TO_INTERNAL = {
    "OpportunityId": "opportunity_id",
    "Opportunity_ID": "opportunity_id",
    "AccountName": "account_name",
    "Account_Name": "account_name",
    "OpportunityName": "opportunity_name",
    "Opportunity_Name": "opportunity_name",
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
    """Normalize supported Salesforce/source field names to canonical names."""
    normalized: dict[str, Any] = {}
    for source, internal in SALESFORCE_TO_INTERNAL.items():
        if source in record and internal not in normalized:
            normalized[internal] = record[source]
    return normalized


def map_to_dbx_draft(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        dbx: record.get(internal)
        for internal, dbx in INTERNAL_TO_DBX_DRAFT.items()
        if internal in record
    }
