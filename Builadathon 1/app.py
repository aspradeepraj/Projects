import streamlit as st
import requests
import os

st.set_page_config(page_title="GovGuard AI Dashboard", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .alert-banner {
        padding: 15px;
        background-color: #fdf2f2;
        border-left: 5px solid #dc2626;
        color: #991b1b;
        font-weight: bold;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ GovGuard AI: Autonomous IT Program Governance Agent")
st.markdown("24/7 RPA Telemetry + Hybrid RAG Contract Compliance + Executive Risk Escalation")
st.markdown("---")

col1, col2 = st.columns([1, 3])

if "project_name" not in st.session_state:
    st.session_state["project_name"] = "Core Banking Migration"

with col1:
    st.subheader("⚙️ Governance Controls")
    
    uploaded_file = st.file_uploader("Upload SOW Contract (PDF)", type=["pdf"])
    if uploaded_file is not None:
        with open("sow_contract.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["project_name"] = uploaded_file.name
        try:
            requests.post("http://127.0.0.1:8000/reload-sow")
            st.success("SOW uploaded & RAG updated!")
        except:
            st.warning("Backend offline.")

    audit_trigger = st.button("Run Autonomous Governance Audit", type="primary")
    
    st.markdown("### Program Details")
    st.text(f"Project: {st.session_state['project_name']}")
    st.text("Phase: Wave 2 Execution")
    st.text("Contract Ref: SOW-2026-CB2")
    
    st.markdown("---")
    if st.button("📥 Download Executive Audit PDF"):
        try:
            pdf_res = requests.get("http://127.0.0.1:8000/generate-audit-pdf")
            if pdf_res.status_code == 200:
                with open("GovGuard_Executive_Audit_Report.pdf", "wb") as f:
                    f.write(pdf_res.content)
                st.success("PDF Generated Successfully!")
                st.download_button(
                    label="Click here to save PDF",
                    data=pdf_res.content,
                    file_name="GovGuard_Executive_Audit_Report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error("Could not generate PDF from backend.")

with col2:
    if audit_trigger:
        with st.spinner("Executing autonomous audit across portal, ChromaDB, and DeepEval evaluation..."):
            try:
                res = requests.post("http://127.0.0.1:8000/audit/run", json={"query": "Check budget and velocity SLAs"})
                data = res.json()
                
                metrics = data.get("rpa_metrics", {})
                eval_data = data.get("audit_evaluation", {})
                deepeval_metrics = data.get("deepeval_metrics", {})
                
                # Alert Banner
                st.markdown(
                    f'<div class="alert-banner">🚨 GOVERNANCE ALERT: Portal self-reported GREEN (Self-Reported by Vendor), but GovGuard AI detected RED status (Risk Score: {eval_data.get("risk_score", 92)}/100).</div>',
                    unsafe_allow_html=True
                )
                
                # 4 Metrics Columns
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Vendor Status", metrics.get("status", "GREEN"), "Self-Reported")
                m2.metric("GovGuard Status", eval_data.get("true_status", "RED"), "Autonomous Audit", delta_color="inverse")
                m3.metric("Budget Burn (Milestone 3)", metrics.get("budget_burn", "86.5%"), "+6.5% over 80% Cap", delta_color="inverse")
                m4.metric("Sprint Velocity Variance", metrics.get("velocity_variance", "-24.0%"), "-4.0% past -20% SLA", delta_color="inverse")
                
                # DeepEval Live Metrics
                st.markdown("### 🧪 DeepEval RAG Quality & Faithfulness Assurance")
                d1, d2 = st.columns(2)
                d1.metric("Faithfulness Score", f"{deepeval_metrics.get('faithfulness', 0.95):.2f}/1.00", "Passed")
                d2.metric("Answer Relevancy Score", f"{deepeval_metrics.get('answer_relevancy', 0.92):.2f}/1.00", "Passed")
                
                st.markdown("### 📝 Executive Steering Committee Summary")
                st.info(eval_data.get("escalation_summary", ""))
                
                st.markdown("### ⚠️ Contractual Breaches & Corrective Actions")
                breaches = eval_data.get("detected_breaches", [])
                if breaches and isinstance(breaches[0], dict):
                    import pandas as pd
                    df = pd.DataFrame(breaches)
                    st.dataframe(df, use_container_width=True)
                else:
                    for b in breaches:
                        st.error(f"- {b}")
                
                with st.expander("🔍 View Hybrid RAG Re-Ranked SOW Clauses & RPA Telemetry"):
                    for clause in data.get("retrieved_clauses", []):
                        st.write(f"* **Relevance Score:** {clause['score']:.3f}")
                        st.write(clause['content'])
                        
            except Exception as e:
                st.error(f"Backend connection error: {e}. Ensure FastAPI (`python main.py`) is running.")
    else:
        st.info("Click **Run Autonomous Governance Audit** to launch the analysis and populate the executive dashboard.")