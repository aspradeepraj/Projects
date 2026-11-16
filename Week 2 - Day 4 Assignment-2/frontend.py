import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF Vector DB Manager", layout="wide")
st.title("📄 PDF to FAISS Vector DB Pipeline")

# Create two tabs for the two pipelines
tab1, tab2 = st.tabs(["📤 Pipeline 1: Upload & Index PDF", "🔍 Pipeline 2: Search Vector DB"])

# ==========================================
# TAB 1: UPLOAD PIPELINE
# ==========================================
with tab1:
    st.header("Upload PDF to Vector Database")
    st.write("Upload a PDF file to load, split, embed, and store it into the local FAISS file.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process & Store in FAISS", type="primary"):
            with st.spinner("Processing PDF (Loading -> Splitting -> Embedding -> Saving)..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(f"{BACKEND_URL}/upload-pdf", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['message']}")
                        st.info(f"**File:** {data['filename']} | **Chunks Stored:** {data['chunks_added']}")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to FastAPI backend. Make sure it is running.")

# ==========================================
# TAB 2: FETCH & DISPLAY PIPELINE
# ==========================================
with tab2:
    st.header("Fetch & Display from FAISS")
    st.write("Query the FAISS vector database to retrieve and inspect matching document chunks.")

    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("Enter your search query:", placeholder="e.g., What are the key findings?")
    with col2:
        top_k = st.number_input("Top K results", min_value=1, max_value=10, value=3)

    if st.button("Fetch from Vector DB", type="primary"):
        if not query.strip():
            st.warning("Please enter a search query.")
        else:
            with st.spinner("Searching FAISS index..."):
                try:
                    payload = {"query": query, "top_k": top_k}
                    response = requests.post(f"{BACKEND_URL}/search", json=payload)

                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        if not results:
                            st.info("No matching chunks found.")
                        else:
                            st.subheader(f"Top {len(results)} Matching Chunks")
                            for i, item in enumerate(results, 1):
                                source = item["metadata"].get("source", "Unknown")
                                page = item["metadata"].get("page", "N/A")
                                score = round(item["distance_score"], 4)

                                with st.expander(f"Result #{i} | Page: {page} | L2 Distance: {score}", expanded=True):
                                    st.markdown(item["content"])
                                    st.caption(f"Metadata: {item['metadata']}")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to FastAPI backend. Make sure it is running.")