from __future__ import annotations

from domain.models import Deal


def is_eligible(deal: Deal) -> bool:
    return (
        deal.partner.strip() == "Databricks"
        and deal.registration_required
        and deal.registration_status.strip().lower() != "registered"
    )


def eligibility_reason(deal: Deal) -> str:
    if deal.partner.strip() != "Databricks":
        return f"Partner is '{deal.partner or 'blank'}', not Databricks"
    if not deal.registration_required:
        return "Registration is not required for this deal"
    if deal.registration_status.strip().lower() == "registered":
        return "Deal is already registered"
    return ""
