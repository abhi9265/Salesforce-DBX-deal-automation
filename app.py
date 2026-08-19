from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from adapters.salesforce.mock_salesforce import MockSalesforceAdapter
from audit.repository import AuditRepository
from services.workflow import DealRegistrationWorkflow


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "sample_opportunities.csv"

st.set_page_config(page_title="Salesforce–DBX Deal Automation", layout="wide")
st.title("Salesforce–DBX Deal Automation")
st.caption("Rules-driven deal registration readiness workflow — local MVP")

adapter = MockSalesforceAdapter(DATA_FILE)
audit = AuditRepository(ROOT / "data" / "audit.db")
workflow = DealRegistrationWorkflow(audit)
deals = adapter.list_opportunities()

rows = []
for deal in deals:
    request = workflow.evaluate(deal)
    rows.append(
        {
            "Opportunity": deal.opportunity_id,
            "Account": deal.account_name,
            "Amount": deal.amount,
            "Partner": deal.partner,
            "Eligibility": "Eligible" if request.status.value != "NOT_ELIGIBLE" else "Not eligible",
            "Validation": request.status.value,
            "Reason": "; ".join(request.validation_errors),
        }
    )

frame = pd.DataFrame(rows)
st.metric("Opportunities", len(frame))
st.metric("Ready / Validated", int((frame["Validation"] == "VALIDATED").sum()))
st.metric("Validation failures", int((frame["Validation"] == "VALIDATION_FAILED").sum()))

st.subheader("Deal readiness")
st.dataframe(frame, use_container_width=True, hide_index=True)

st.subheader("Review a deal")
selected_id = st.selectbox("Opportunity", frame["Opportunity"].tolist())
selected = next(deal for deal in deals if deal.opportunity_id == selected_id)
request = workflow.evaluate(selected)

st.json(request.to_dict())

if request.status.value == "VALIDATED":
    if st.button("Move to review"):
        workflow.prepare_for_review(request)
        st.success(f"{selected_id} is ready for manager review.")

if request.status.value == "READY_FOR_REVIEW":
    approver = st.text_input("Approver identity")
    if st.button("Approve"):
        if not approver.strip():
            st.error("Approver identity is required.")
        else:
            workflow.approve(request, approver.strip())
            st.success(f"{selected_id} approved by {approver.strip()}.")
