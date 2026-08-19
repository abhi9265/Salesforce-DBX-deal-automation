from __future__ import annotations

from typing import Any, Mapping

from adapters.salesforce.rest_client import SalesforceRestClient
from domain.models import Deal


DEFAULT_OPPORTUNITY_FIELDS = (
    "Id,Account.Name,Name,Country__c,Amount,Industry,Partner__c,"
    "CloseDate,Registration_Required__c,Registration_Status__c"
)


class SalesforceOpportunityAdapter:
    """Reads Salesforce opportunities and converts them into canonical Deals."""

    def __init__(self, client: SalesforceRestClient) -> None:
        self.client = client

    def fetch_opportunities(self, fields: str = DEFAULT_OPPORTUNITY_FIELDS) -> list[Deal]:
        records = self.client.query(
            f"SELECT {fields} FROM Opportunity ORDER BY LastModifiedDate DESC"
        )
        return [self._to_deal(record) for record in records]

    @staticmethod
    def _to_deal(record: Mapping[str, Any]) -> Deal:
        account = record.get("Account") or {}
        return Deal(
            opportunity_id=str(record.get("Id", "")),
            account_name=str(account.get("Name", "")),
            opportunity_name=str(record.get("Name", "")),
            country=str(record.get("Country__c", "")),
            amount=float(record.get("Amount") or 0),
            industry=str(record.get("Industry", "")),
            partner=str(record.get("Partner__c", "")),
            close_date=str(record.get("CloseDate", "")),
            registration_required=bool(record.get("Registration_Required__c", False)),
            registration_status=str(record.get("Registration_Status__c", "Not Registered")),
        )
