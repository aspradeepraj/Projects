import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv(override=True)

st.set_page_config(page_title="Knowledge Graph RAG Studio", layout="wide")
st.title("Knowledge Graph RAG with Neo4j AuraDB")

# Connect to Neo4j AuraDB
@st.cache_resource
def get_neo4j_connection():
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE")
    )

db = get_neo4j_connection()
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# --- SIDEBAR: Document Upload & Graph Extraction ---
with st.sidebar:
    st.header("1. Build Knowledge Graph")
    uploaded_file = st.file_uploader("Upload a .txt file (optional)", type=["txt"])
    clear_db = st.checkbox("Clear existing Neo4j graph before upload", value=True)
    chunk_size = st.slider("Chunk Size", min_value=200, max_value=2000, value=1000, step=100)

    if st.button("Extract & Store in Neo4j", type="primary"):
        with st.spinner("Extracting entities and saving to Neo4j AuraDB..."):
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    file_path = tmp.name
            else:
                file_path = "sample.txt"

            loader = TextLoader(file_path, encoding="utf-8")
            raw_documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
            documents = text_splitter.split_documents(raw_documents)

            graph_transformer = LLMGraphTransformer(llm=llm)
            graph_documents = graph_transformer.convert_to_graph_documents(documents)

            if clear_db:
                db.query("MATCH (n) DETACH DELETE n")
            db.add_graph_documents(graph_documents, include_source=True)
            db.refresh_schema()

            st.success(f"Stored graph from {len(documents)} chunk(s) into Neo4j!")

# --- MAIN AREA: Natural Language Q&A ---
st.subheader("Ask Questions (Graph RAG)")
user_question = st.text_input(
    "Enter your question:",
    value="What is Python and how does it relate to the other topics?"
)

if st.button("Ask Graph", type="primary"):
    with st.spinner("Generating Cypher query and retrieving answer..."):
        db.refresh_schema()

        CYPHER_TEMPLATE = """Task: Generate a Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
CRITICAL RULE: Do NOT use UNION unless strictly necessary. If you use UNION, every RETURN clause MUST use identical column aliases.

Schema:
{schema}

The question is:
{question}"""

        cypher_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template=CYPHER_TEMPLATE
        )

        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=db,
            cypher_prompt=cypher_prompt,
            validate_cypher=True,
            return_intermediate_steps=True,
            allow_dangerous_requests=True
        )

        response = chain.invoke({"query": user_question})
        generated_cypher = response["intermediate_steps"][0]["query"]

        st.markdown("### Final Answer")
        st.write(response["result"])

        with st.expander("View Generated Cypher Query"):
            st.code(generated_cypher, language="cypher")