import os
import re
import json
import textwrap
import warnings
import tempfile

import streamlit as st
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from streamlit_agraph import agraph, Node, Edge, Config

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv(override=True)

st.set_page_config(page_title="Knowledge Graph RAG Studio", layout="wide")
st.title("Knowledge Graph RAG with Neo4j AuraDB")


@st.cache_resource
def get_neo4j_connection():
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE"),
    )


db = get_neo4j_connection()
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")


# --- 1. GUARDRAILS ------------------------------------------------------------
def check_input_guardrails(query):
    cleaned = query.strip()
    if not cleaned:
        return False, "Input Guardrail Blocked: Please enter a valid question."
    if len(cleaned) > 500:
        return False, "Input Guardrail Blocked: Question exceeds the 500-character limit."

    blocked_patterns = [
        r"ignore (all )?previous instructions",
        r"system prompt",
        r"jailbreak",
        r"\b(detach delete|drop database|delete\s+\*)\b",
    ]
    for pattern in blocked_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False, f"Input Guardrail Blocked: Unsafe pattern detected ({pattern})."

    return True, "Passed"


def check_output_guardrails(context_rows):
    if not context_rows:
        return (
            False,
            "Output Guardrail Triggered: No matching entities or documents found in Neo4j.",
        )
    has_data = any(row.get("entity") or row.get("source_text") for row in context_rows)
    if not has_data:
        return False, "Output Guardrail Triggered: Retrieved graph records were empty."
    return True, "Passed"


# --- 2. AUTOMATED RAG EVALS (LLM-AS-A-JUDGE) ----------------------------------
def evaluate_rag_response(question, context, answer):
    system_msg = (
        "You are an impartial RAG Evaluation Judge. Score the response from 1 to 5 (5 = best) on three metrics:\n"
        "1. faithfulness: Is every claim in the Answer strictly supported by the Context without outside hallucination?\n"
        "2. relevance: Does the Answer directly and completely address the Question?\n"
        "3. context_precision: Did the retrieved Context contain the right information needed to answer the Question?\n"
        "Return ONLY valid JSON with keys: 'faithfulness', 'relevance', 'context_precision', and 'reason' (one short sentence)."
    )
    eval_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            (
                "human",
                "Question: {question}\n\nRetrieved Context:\n{context}\n\nGenerated Answer:\n{answer}",
            ),
        ]
    )
    eval_chain = eval_prompt | llm | StrOutputParser()
    raw_eval = eval_chain.invoke(
        {"question": question, "context": context, "answer": answer}
    )
    try:
        cleaned_json = raw_eval.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(cleaned_json)
    except Exception:
        return {
            "faithfulness": 0,
            "relevance": 0,
            "context_precision": 0,
            "reason": "Could not parse evaluation output.",
        }


# --- 3. VISUAL LABEL WRAPPER ----------------------------------------------------
def wrap_label(text, width=22):
    return "\n".join(textwrap.wrap(str(text), width=width))


def sanitize_keyword(raw: str) -> str:
    """Reduce the LLM keyword to a safe alphanumeric token for Cypher CONTAINS."""
    return re.sub(r"[^a-z0-9 ]", "", raw.lower()).strip()


# --- SIDEBAR: Document Upload & Graph Extraction --------------------------------
with st.sidebar:
    st.header("1. Build Knowledge Graph")
    uploaded_file = st.file_uploader("Upload a .txt file (optional)", type=["txt"])
    clear_db = st.checkbox("Clear existing Neo4j graph before upload", value=True)
    chunk_size = st.slider("Chunk Size", min_value=200, max_value=2000, value=1000, step=100)

    if st.button("Extract & Store in Neo4j", type="primary"):
        with st.spinner("Extracting concise entities and saving to Neo4j AuraDB..."):
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    file_path = tmp.name
            else:
                file_path = "sample.txt"

            with open(file_path, "r", encoding="utf-8") as f:
                raw_documents = [Document(page_content=f.read(), metadata={"source": file_path})]

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=50
            )
            documents = text_splitter.split_documents(raw_documents)

            extraction_sys = (
                "You are an expert knowledge graph extractor. Extract entities and relationships strictly from the provided text.\n"
                "CRITICAL RULE: Keep all node IDs concise (1 to 3 words maximum, e.g., 'API', 'Software Applications', 'Python', 'Guido van Rossum'). Never use full sentences as node names."
            )
            extraction_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", extraction_sys),
                    ("human", "{input}"),
                ]
            )

            graph_transformer = LLMGraphTransformer(llm=llm, prompt=extraction_prompt)
            graph_documents = graph_transformer.convert_to_graph_documents(documents)

            if clear_db:
                db.query("MATCH (n) DETACH DELETE n")
            db.add_graph_documents(graph_documents, include_source=True)
            db.refresh_schema()

            st.success(f"Stored clean graph from {len(documents)} chunk(s) into Neo4j!")

# --- MAIN AREA: Natural Language Q&A + Guardrails + Evals + Clean Visual Graph ---
st.subheader("Ask Questions (Graph RAG)")
user_question = st.text_input("Enter your question:", value="What is an API?")

if st.button("Ask Graph", type="primary"):
    input_ok, input_msg = check_input_guardrails(user_question)
    if not input_ok:
        st.error(input_msg)
        st.stop()

    with st.spinner("Querying Neo4j Knowledge Graph & Running Guardrails/Evals..."):
        try:
            keyword_prompt = (
                "Extract the single main entity or topic keyword (1-2 words, lowercase, "
                f"no punctuation) from this question: {user_question}"
            )
            keyword = sanitize_keyword(llm.invoke(keyword_prompt).content)

            # Parameterized Cypher — no f-string injection of the LLM keyword
            context_cypher = """
                OPTIONAL MATCH (d:Document)-[:MENTIONS]-(n)
                WHERE toLower(n.id) CONTAINS $keyword
                OPTIONAL MATCH (n)-[r]-(m)
                WHERE NOT m:Document
                RETURN DISTINCT n.id AS entity, type(r) AS relationship,
                                  m.id AS related_entity, d.text AS source_text
                LIMIT 25
            """
            context_rows = db.query(context_cypher, params={"keyword": keyword})

            output_ok, output_msg = check_output_guardrails(context_rows)
            if not output_ok:
                st.warning(output_msg)
                st.stop()

            context_str = str(context_rows)
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a helpful Knowledge Graph RAG assistant. Answer the user's "
                        "question thoroughly and accurately using ONLY the retrieved Neo4j "
                        "graph relationships and source text below. Do not add outside information.\n\n"
                        "Retrieved Context:\n{context}",
                    ),
                    ("human", "{question}"),
                ]
            )
            qa_chain = qa_prompt | llm | StrOutputParser()
            final_answer = qa_chain.invoke({"context": context_str, "question": user_question})

            eval_scores = evaluate_rag_response(user_question, context_str, final_answer)

            st.success("Guardrails Passed: Input safe & answer strictly grounded in Neo4j context.")
            st.markdown("### Final Answer")
            st.write(final_answer)

            st.markdown("### RAG Evaluation Scores (LLM-as-a-Judge)")
            m1, m2, m3 = st.columns(3)
            m1.metric("Faithfulness (Groundedness)", f"{eval_scores.get('faithfulness', 0)} / 5")
            m2.metric("Answer Relevance", f"{eval_scores.get('relevance', 0)} / 5")
            m3.metric("Context Precision", f"{eval_scores.get('context_precision', 0)} / 5")
            st.caption(f"**Judge Summary:** {eval_scores.get('reason', '')}")

            visual_cypher = f"""MATCH (n)-[r]-(m)
WHERE NOT n:Document AND NOT m:Document
  AND (toLower(n.id) CONTAINS '{keyword}' OR toLower(m.id) CONTAINS '{keyword}')
RETURN DISTINCT n, r, m"""

            with st.expander("View Neo4j Visual Cypher Query", expanded=False):
                st.code(visual_cypher, language="cypher")

            graph_query = """
                MATCH (n)-[r]-(m)
                WHERE NOT n:Document AND NOT m:Document
                  AND (toLower(n.id) CONTAINS $keyword OR toLower(m.id) CONTAINS $keyword)
                RETURN DISTINCT n.id AS source, type(r) AS rel, m.id AS target
            """
            graph_rows = db.query(graph_query, params={"keyword": keyword})

            if graph_rows:
                st.markdown("### Interactive Knowledge Graph View")
                nodes_dict = {}
                edges = []
                seen_edges = set()

                for row in graph_rows:
                    src = row.get("source")
                    tgt = row.get("target")
                    rel = row.get("rel")
                    if not src or not tgt:
                        continue

                    if src not in nodes_dict:
                        is_main = keyword in src.lower()
                        nodes_dict[src] = Node(
                            id=src,
                            label=wrap_label(src),
                            size=32 if is_main else 24,
                            color="#2563EB" if is_main else "#10B981",
                            font={"size": 14, "color": "#1F2937", "face": "arial"},
                        )
                    if tgt not in nodes_dict:
                        is_main = keyword in tgt.lower()
                        nodes_dict[tgt] = Node(
                            id=tgt,
                            label=wrap_label(tgt),
                            size=32 if is_main else 24,
                            color="#2563EB" if is_main else "#10B981",
                            font={"size": 14, "color": "#1F2937", "face": "arial"},
                        )

                    edge_key = (src, rel, tgt)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(
                            Edge(
                                source=src,
                                label=rel,
                                target=tgt,
                                color="#64748B",
                                font={"size": 12, "color": "#334155", "align": "top"},
                            )
                        )

                config = Config(
                    width="100%",
                    height=520,
                    directed=True,
                    physics={
                        "enabled": True,
                        "barnesHut": {
                            "gravitationalConstant": -4500,
                            "centralGravity": 0.2,
                            "springLength": 220,
                            "springConstant": 0.04,
                            "avoidOverlap": 1,
                        },
                    },
                    hierarchical=False,
                )
                agraph(nodes=list(nodes_dict.values()), edges=edges, config=config)

        except Exception as e:
            st.error(f"Query failed: {e}")