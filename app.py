from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from adapters.databricks.registration import DatabricksRegistrationAdapter
from adapters.salesforce.mock_salesforce import MockSalesforceAdapter
from audit.processed_deals import SQLiteProcessedDealStore
from audit.repository import AuditRepository
from services.mapping import map_to_dbx_draft
from services.registration_processor import RegistrationProcessor
from services.workflow import DealRegistrationWorkflow


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "sample_opportunities.csv"
AUDIT_FILE = ROOT / "data" / "audit.db"
IDEMPOTENCY_FILE = ROOT / "data" / "idempotency.db"

st.set_page_config(page_title="Salesforce–DBX Deal Automation", layout="wide")
st.title("Salesforce–DBX Deal Automation")
st.caption("Rules-driven deal registration readiness workflow — local MVP")

adapter = MockSalesforceAdapter(DATA_FILE)
audit = AuditRepository(AUDIT_FILE)
workflow = DealRegistrationWorkflow(audit)
processor = RegistrationProcessor(
    SQLiteProcessedDealStore(IDEMPOTENCY_FILE),
    DatabricksRegistrationAdapter(),
    audit=audit,
)
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
            "Eligibility": (
                "Eligible"
                if request.status.value != "NOT_ELIGIBLE"
                else "Not eligible"
            ),
            "Validation": request.status.value,
            "Reason": "; ".join(request.validation_errors),
        }
    )

frame = pd.DataFrame(rows)
metric_cols = st.columns(3)
metric_cols[0].metric("Opportunities", len(frame))
metric_cols[1].metric(
    "Ready / Validated",
    int((frame["Validation"] == "VALIDATED").sum()),
)
metric_cols[2].metric(
    "Validation failures",
    int((frame["Validation"] == "VALIDATION_FAILED").sum()),
)

st.subheader("Deal readiness")
st.dataframe(frame, use_container_width=True, hide_index=True)

st.subheader("Registration workflow")
selected_id = st.selectbox("Opportunity", frame["Opportunity"].tolist())
selected = next(deal for deal in deals if deal.opportunity_id == selected_id)

if "requests" not in st.session_state:
    st.session_state.requests = {}
request = st.session_state.requests.get(selected_id)
if request is None:
    request = workflow.evaluate(selected)
    st.session_state.requests[selected_id] = request

st.write(f"**Current status:** `{request.status.value}`")
if request.validation_errors:
    st.warning("; ".join(request.validation_errors))

if request.status.value == "VALIDATED":
    if st.button("Move to review"):
        workflow.prepare_for_review(request)
        audit.save_request(request)
        st.rerun()

if request.status.value == "READY_FOR_REVIEW":
    approver = st.text_input("Approver identity")
    if st.button("Approve"):
        if not approver.strip():
            st.error("Approver identity is required.")
        else:
            workflow.approve(request, approver.strip())
            audit.save_request(request)
            st.rerun()

if request.status.value == "APPROVED":
    payload = map_to_dbx_draft(
        {
            "account_name": selected.account_name,
            "opportunity_name": selected.opportunity_name,
            "country": selected.country,
            "amount": selected.amount,
            "industry": selected.industry,
            "partner": selected.partner,
            "close_date": selected.close_date,
        }
    )
    with st.expander("Mapped registration payload"):
        st.json(payload)
    if st.button("Submit to Databricks"):
        result = processor.process(selected, request, payload)
        if result.processed:
            st.success(
                f"Registration completed: {request.registration_number}"
            )
            st.rerun()
        elif result.reason == "unchanged_source_version":
            st.info("This source version has already been processed.")
        else:
            st.error(result.reason or "Registration submission failed.")

if request.status.value in {
    "SUBMITTED",
    "REGISTERED",
    "SUBMISSION_FAILED",
    "SUBMISSION_UNKNOWN",
}:
    if request.registration_number:
        st.success(f"Registration number: {request.registration_number}")

st.subheader("Request state")
st.json(request.to_dict())

st.subheader("Audit history")
history = audit.history(request.request_id)
if history:
    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
else:
    st.info("No persisted events for this request yet.")
