import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="GovGuard AI | Program Governance", page_icon="🛡️", layout="wide")

st.title("🛡️ GovGuard AI: Autonomous IT Program Governance Agent")
st.caption("24/7 RPA Telemetry + Hybrid RAG Contract Compliance + Guardrailed Risk Escalation")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Governance Controls")
    api_url = st.text_input("FastAPI Endpoint", "http://127.0.0.1:8000/audit/run")


    custom_prompt = st.text_area(
        "Audit Focus / Steering Query",
        value="Verify Milestone 2 budget burn, sprint velocity variance, and unapproved scope changes against SOW clauses."
    )
    run_btn = st.button("🚀 Run Autonomous Governance Audit", type="primary", use_container_width=True)

if run_btn:
    with st.spinner("🤖 Playwright RPA scraping legacy portal & Hybrid RAG verifying SOW clauses..."):
        try:
            res = requests.post(api_url, json={"custom_question": custom_prompt}, timeout=30)
            if res.status_code != 200:
                st.error(f"Audit Blocked / Failed: {res.json().get('detail')}")
            else:
                data = res.json()
                metrics = data["live_metrics"]
                report = data["audit_report"]

                # Top Alert Banner for Status Misreporting
                if report.get("status_discrepancy_detected"):
                    st.error(
                        f"🚨 **GOVERNANCE ALERT:** Portal self-reported **{metrics['portal_reported_status']}**, "
                        f"but GovGuard AI detected **{report['true_rag_status']}** status (Risk Score: **{report['risk_score']}/100**)."
                    )

                # KPI Row
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("True Governance Status", report["true_rag_status"], delta="Escalation Required", delta_color="inverse")
                col2.metric("Budget Burn (Milestone 2)", f"{metrics['budget_burn_pct']}%", delta="+6.5% over 80% cap", delta_color="inverse")
                col3.metric("Velocity Variance", f"{metrics['velocity_variance_pct']}%", delta="-4.0% past -20% SLA", delta_color="inverse")
                col4.metric("Unapproved Scope Creep", f"{metrics['unapproved_scope_creep_pct']}%", delta="+6.2% past 5% cap", delta_color="inverse")

                st.divider()

                # Executive Summary & Breaches Table
                st.subheader("📋 Executive Steering Committee Summary")
                st.info(report["executive_summary"])

                st.subheader("⚠️ Contractual Breaches & Corrective Actions")
                if report.get("breaches"):
                    df_breaches = pd.DataFrame(report["breaches"])
                    st.dataframe(df_breaches, use_container_width=True, hide_index=True)

                # RAG Evidence Expander
                with st.expander("🔍 View Hybrid RAG Re-Ranked SOW Evidence & RPA Telemetry"):
                    st.json(metrics)
                    for idx, clause in enumerate(data["retrieved_clauses"], 1):
                        st.markdown(f"**Verified Clause {idx}:** {clause}")

        except requests.exceptions.ConnectionError:
            st.warning("⚠️ FastAPI backend is offline. Start it using: `uvicorn backend.main:app --reload`")
else:
    st.info("👈 Click **Run Autonomous Governance Audit** in the sidebar to trigger the RPA + Hybrid RAG pipeline.")
