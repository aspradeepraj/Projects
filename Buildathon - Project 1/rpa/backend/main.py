import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

from rpa.legacy_portal_bot import fetch_legacy_portal_metrics
from rag.hybrid_retriever import HybridGovernanceRAG
from rag.guardrails import GovernanceGuardrails

load_dotenv()

app = FastAPI(title="GovGuard AI Governance Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_engine = HybridGovernanceRAG()
llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0)


class AuditQuery(BaseModel):
    custom_question: str = "Audit current sprint metrics against SOW compliance thresholds."


@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "online", "service": "GovGuard AI Governance Engine"}


@app.post("/audit/run")
def run_autonomous_audit(request: AuditQuery):
    try:
        # 1. Input Guardrails: Block prompt injection & redact PII
        clean_question = GovernanceGuardrails.sanitize_input(request.custom_question)

        # 2. Collect RPA telemetry from legacy portal
        telemetry_data = fetch_legacy_portal_metrics()

        # 3. Retrieve & re-rank SOW contract clauses via Hybrid RAG
        retrieved_docs = rag_engine.retrieve_and_rerank(clean_question)
        clauses_list = [doc.page_content for doc in retrieved_docs]
        contract_context = "\n\n".join(clauses_list)

        # 4. Synthesize structured JSON governance report via LLM
        prompt = (
            "You are an autonomous IT program governance auditor. Evaluate the live program "
            "telemetry against the Statement of Work (SOW) contract clauses and return ONLY valid JSON "
            "(no markdown fences) with these exact keys:\n"
            '- "status_discrepancy_detected": boolean\n'
            '- "true_rag_status": string ("RED", "AMBER", or "GREEN")\n'
            '- "risk_score": integer (0 to 100)\n'
            '- "executive_summary": string\n'
            '- "breaches": list of objects, each with keys "Clause", "Metric", "Threshold", "Actual", "Corrective_Action"\n\n'
            f"Audit Focus: {clean_question}\n"
            f"Live RPA Telemetry: {json.dumps(telemetry_data)}\n"
            f"SOW Contract Clauses:\n{contract_context}"
        )
        ai_response = llm.invoke(prompt)
        raw_text = (
            ai_response.content.strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )
        report_json = json.loads(raw_text)

        return {
            "live_metrics": telemetry_data,
            "audit_report": report_json,
            "retrieved_clauses": clauses_list,
        }

    except ValueError as security_err:
        raise HTTPException(status_code=400, detail=str(security_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))