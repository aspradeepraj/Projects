# Multi-PDF RAG Assistant with Source Citations

A Retrieval-Augmented Generation (RAG) web application built with **Streamlit**, **LangChain**, **FAISS**, and **OpenAI**. Users can upload multiple PDFs simultaneously, index them into a unified vector store, and ask questions across all documents with exact file name and page number citations.

---

## Features

* **Batch PDF Ingestion:** Upload and process multiple PDF files in a single action.
* **Unified Vector Store:** Chunks and embeds all documents into a single in-memory FAISS index persisted via `st.session_state`.
* **Accurate Source Tracking:** Preserves original file names and human-readable (1-indexed) page numbers across text splitting.
* **Conflict Detection:** Prompt-engineered to explicitly highlight contradictions when uploaded documents disagree rather than silently choosing one source.
* **Tunable Chunking & Debug View:** Includes sidebar sliders for chunk size/overlap and an expandable raw chunk inspector to evaluate retrieval precision.

---

## Project Structure

```text
multi-rag/
├── .env                # Environment variables (API key)
├── .gitignore          # Excludes .env and virtual environment from Git
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
└── rag_app.py          # Main Streamlit application
```

---

## Setup & Installation

### 1. Clone or Navigate to the Project Directory
```bash
cd multi-rag
```

### 2. Create and Activate a Virtual Environment
* **Mac / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
* **Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key
Create a `.env` file in the root directory and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 5. Run the Application
```bash
streamlit run rag_app.py
```

---

## Architectural Notes ("Think It Through")

### Handling Contradictions Across Documents
When querying multiple documents (e.g., different policy versions or conflicting reports), standard RAG pipelines often blend facts or silently favor one chunk. To prevent this:
1. Every retrieved chunk is wrapped with explicit metadata headers (`[File: <name>, Page: <number>]`) before being passed to the LLM.
2. The system prompt instructs the model to act as a neutral analyst—if sources conflict, it must explicitly state that the documents disagree and present each viewpoint alongside its exact file and page citation.

### Evaluating Chunk Size & Citation Spread
* **Why Page Spread Matters:** If a simple factual query cites 5 different pages across a document, the `chunk_size` is likely too small (splitting cohesive paragraphs across boundaries) or the retriever's `k` value is pulling in low-relevance noise.
* **Tuning Approach:** A default `chunk_size` of `1000` characters with a `150`-character overlap balances context preservation with retrieval specificity. Users can adjust these values in the sidebar and use the **Inspect Retrieved Chunks** panel to verify whether retrieved segments contain complete ideas.