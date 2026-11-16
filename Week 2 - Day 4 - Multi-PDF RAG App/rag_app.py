import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

# 1. Load API key from .env file (override=True ignores stale Windows keys)
load_dotenv(override=True)

st.set_page_config(page_title="Multi-PDF RAG with Sources", layout="wide")
st.title("📚 Multi-PDF RAG Assistant")

if not os.environ.get("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found. Please add it to your .env file.")
    st.stop()

# 2. Keep vector database in session memory across reruns
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

# 3. Sidebar: Upload multiple PDFs & build FAISS index
with st.sidebar:
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )
    chunk_size = st.slider("Chunk Size (characters)", 500, 2000, 1000, 100)
    chunk_overlap = st.slider("Chunk Overlap", 50, 400, 150, 50)

    if st.button("Build Vector Store", type="primary") and uploaded_files:
        with st.spinner("Processing and indexing PDFs..."):
            all_docs = []

            for uploaded_file in uploaded_files:
                # Save uploaded bytes to a temp file so PyPDFLoader can read it
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                try:
                    docs = PyPDFLoader(tmp_path).load()
                    # Replace random temp filename with the real PDF filename
                    for doc in docs:
                        doc.metadata["source"] = uploaded_file.name
                    all_docs.extend(docs)
                finally:
                    os.remove(tmp_path)

            # Split documents into chunks while preserving file & page metadata
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            chunks = splitter.split_documents(all_docs)

            # Embed chunks and store them in one FAISS vector database
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            st.session_state.vector_store = FAISS.from_documents(chunks, embeddings)
            st.session_state.chunk_count = len(chunks)

            st.success(f"Indexing complete! **{st.session_state.chunk_count} chunks** indexed across {len(uploaded_files)} file(s).")

    if st.session_state.chunk_count > 0:
        st.info(f"Active Index: {st.session_state.chunk_count} chunks ready.")

# 4. Main Area: Ask questions & show sources
st.header("2. Ask Questions Across Your Documents")
query = st.text_input("Enter your question:")

if query:
    if st.session_state.vector_store is None:
        st.warning("Please upload PDFs and click 'Build Vector Store' in the sidebar first.")
    else:
        with st.spinner("Searching documents and generating answer..."):
            retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 5})
            retrieved_docs = retriever.invoke(query)

            formatted_context = ""
            sources_set = set()

            for i, doc in enumerate(retrieved_docs):
                file_name = doc.metadata.get("source", "Unknown File")
                page_num = doc.metadata.get("page", 0) + 1  # Convert 0-based index to 1-based page
                sources_set.add((file_name, page_num))
                formatted_context += f"\n--- Excerpt {i+1} [File: {file_name}, Page: {page_num}] ---\n{doc.page_content}\n"

            prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "You are a precise research assistant analyzing multiple documents. "
                 "Answer the user's question using ONLY the provided context excerpts. "
                 "CRITICAL INSTRUCTION: If the documents contain conflicting or contradictory information, "
                 "do NOT quietly pick one. Explicitly state that the documents disagree, and clearly present "
                 "what each source says along with its file name and page number. "
                 "If the answer is not in the context, state that you cannot find it in the uploaded files."),
                ("human", "Context:\n{context}\n\nQuestion: {question}")
            ])

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            response = (prompt | llm).invoke({"context": formatted_context, "question": query})

            st.subheader("Answer")
            st.write(response.content)

            st.subheader("Sources Cited")
            for file_name, page_num in sorted(sources_set):
                st.markdown(f"- **{file_name}** — Page {page_num}")
