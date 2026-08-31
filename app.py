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

st.set_page_config(
    page_title="Salesforce → Databricks Deal Operations",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lightweight enterprise-console styling. Business logic remains in the existing
# workflow/services/adapters; this file only controls the Streamlit presentation.
st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 3rem; }
        .console-eyebrow {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.65;
            margin-bottom: 0.2rem;
        }
        .console-subtitle { font-size: 1.05rem; opacity: 0.72; margin-bottom: 1.2rem; }
        .status-card {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(128,128,128,.25);
            border-radius: .75rem;
            background: rgba(128,128,128,.06);
            margin-bottom: .8rem;
        }
        .status-label { font-size: .78rem; opacity: .65; text-transform: uppercase; letter-spacing: .05em; }
        .status-value { font-size: 1.35rem; font-weight: 700; margin-top: .15rem; }
        .flow-step {
            border: 1px solid rgba(128,128,128,.25);
            border-radius: .65rem;
            padding: .7rem .55rem;
            text-align: center;
            min-height: 4.2rem;
        }
        .flow-active { border-color: rgba(46, 204, 113, .75); }
        .flow-done { opacity: .72; }
        .flow-title { font-weight: 700; font-size: .88rem; }
        .flow-state { font-size: .72rem; opacity: .65; margin-top: .2rem; }
        .section-note { opacity: .68; font-size: .9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    evaluated = workflow.evaluate(deal)
    rows.append(
        {
            "Opportunity": deal.opportunity_id,
            "Account": deal.account_name,
            "Amount": deal.amount,
            "Partner": deal.partner,
            "Eligibility": (
                "Eligible"
                if evaluated.status.value != "NOT_ELIGIBLE"
                else "Not eligible"
            ),
            "Validation": evaluated.status.value,
            "Reason": "; ".join(evaluated.validation_errors),
        }
    )

frame = pd.DataFrame(rows)
validated_count = int((frame["Validation"] == "VALIDATED").sum())
failed_count = int((frame["Validation"] == "VALIDATION_FAILED").sum())

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<div class="console-eyebrow">Deal Operations Console</div>', unsafe_allow_html=True)
st.title("Salesforce → Databricks Deal Automation")
st.markdown(
    '<div class="console-subtitle">Rules-driven deal registration workflow for eligibility, validation, approval, registration and audit.</div>',
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# KPI strip
# -----------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Opportunities", len(frame))
k2.metric("Validated", validated_count)
k3.metric("Validation failures", failed_count)
k4.metric("Databricks partner", int((frame["Partner"] == "Databricks").sum()))

st.divider()

# -----------------------------------------------------------------------------
# Interactive workflow — deliberately placed before the large readiness table
# so a recruiter immediately sees that this is an application, not a report.
# -----------------------------------------------------------------------------
st.subheader("Registration workflow")
st.markdown(
    '<div class="section-note">Select a deal and walk it through the same state machine implemented by the domain workflow.</div>',
    unsafe_allow_html=True,
)

selected_id = st.selectbox(
    "Opportunity",
    frame["Opportunity"].tolist(),
    key="opportunity_selector",
)
selected = next(deal for deal in deals if deal.opportunity_id == selected_id)

if "requests" not in st.session_state:
    st.session_state.requests = {}
request = st.session_state.requests.get(selected_id)
if request is None:
    request = workflow.evaluate(selected)
    st.session_state.requests[selected_id] = request

status = request.status.value
status_order = [
    "NEW",
    "ELIGIBLE",
    "VALIDATED",
    "READY_FOR_REVIEW",
    "APPROVED",
    "SUBMITTED",
    "REGISTERED",
]
status_index = status_order.index(status) if status in status_order else 0

# Deal summary
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown('<div class="status-card"><div class="status-label">Account</div><div class="status-value">' + str(selected.account_name) + '</div></div>', unsafe_allow_html=True)
with s2:
    amount = "—" if selected.amount is None else f"${selected.amount:,.0f}"
    st.markdown('<div class="status-card"><div class="status-label">Deal amount</div><div class="status-value">' + amount + '</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="status-card"><div class="status-label">Partner</div><div class="status-value">' + str(selected.partner) + '</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown('<div class="status-card"><div class="status-label">Current status</div><div class="status-value">' + status + '</div></div>', unsafe_allow_html=True)

st.markdown("**Workflow state**")
flow_cols = st.columns(len(status_order))
for i, step in enumerate(status_order):
    with flow_cols[i]:
        if i < status_index:
            icon = "✓"
            css = "flow-step flow-done"
        elif i == status_index:
            icon = "●"
            css = "flow-step flow-active"
        else:
            icon = "○"
            css = "flow-step"
        st.markdown(
            f'<div class="{css}"><div class="flow-title">{icon} {step.replace("_", " ")}</div><div class="flow-state">Step {i + 1}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")

if request.validation_errors:
    st.warning("Validation: " + "; ".join(request.validation_errors))

# State-machine actions. These are the existing workflow operations; only the
# surrounding presentation has been reorganized.
if status == "VALIDATED":
    if st.button("Move to review", type="primary", use_container_width=False):
        workflow.prepare_for_review(request)
        audit.save_request(request)
        st.session_state.requests[selected_id] = request
        st.rerun()

if status == "READY_FOR_REVIEW":
    approver = st.text_input("Approver identity", placeholder="e.g. sales-ops-user")
    if st.button("Approve deal", type="primary", use_container_width=False):
        if not approver.strip():
            st.error("Approver identity is required.")
        else:
            workflow.approve(request, approver.strip())
            audit.save_request(request)
            st.session_state.requests[selected_id] = request
            st.rerun()

if status == "APPROVED":
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
    with st.expander("View mapped Databricks registration payload"):
        st.json(payload)
    if st.button("Submit to Databricks", type="primary"):
        result = processor.process(selected, request, payload)
        if result.processed:
            st.success(f"Registration completed: {request.registration_number}")
            st.session_state.requests[selected_id] = request
            st.rerun()
        elif result.reason == "unchanged_source_version":
            st.info("This source version has already been processed.")
        else:
            st.error(result.reason or "Registration submission failed.")

if status in {"SUBMITTED", "REGISTERED", "SUBMISSION_FAILED", "SUBMISSION_UNKNOWN"}:
    if request.registration_number:
        st.success(f"Registration number: {request.registration_number}")
    if status == "SUBMISSION_UNKNOWN":
        st.warning("Downstream submission outcome is unknown; the workflow does not treat unknown as success.")

# -----------------------------------------------------------------------------
# Request state + audit, grouped into a secondary inspection area.
# -----------------------------------------------------------------------------
st.divider()
state_tab, audit_tab = st.tabs(["Request state", "Audit history"])

with state_tab:
    st.markdown("**Durable workflow state**")
    st.json(request.to_dict())

with audit_tab:
    history = audit.history(request.request_id)
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
    else:
        st.info("No persisted events for this request yet.")

# -----------------------------------------------------------------------------
# Readiness table — useful for operations, but intentionally secondary to the
# interactive workflow above.
# -----------------------------------------------------------------------------
st.divider()
with st.expander("Deal readiness — view all opportunities", expanded=False):
    st.markdown(
        '<div class="section-note">All source opportunities with eligibility and validation outcomes.</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(frame, use_container_width=True, hide_index=True)

st.caption("Demo uses controlled sample Salesforce data and a mock Salesforce adapter; Databricks integration is represented by the adapter boundary.")
