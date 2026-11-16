import json

# Read your existing rag_app.py directly so there are no escaping issues
with open("rag_app.py", "r", encoding="utf-8") as f:
    app_code = "%%writefile rag_app.py\n" + f.read()

def md_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}

def code_cell(code):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": code.splitlines(keepends=True)}

cells = [
    md_cell("""# 📚 Multi-PDF RAG App with Source Citations — Fresher's Guide

Welcome! This notebook builds a **Retrieval-Augmented Generation (RAG)** web app that lets you upload multiple PDFs at once, ask questions across all of them simultaneously, and get answers backed by **exact file names and page numbers**.

---
## 🧠 How RAG Works (Simple Analogy)
Imagine you have 10 textbooks and someone asks a specific question:
1. **Without RAG (Normal ChatGPT):** It answers only from general training memory and cannot read your private PDFs.
2. **With RAG (Our App):** It flips straight to the exact pages mentioning the topic, reads those paragraphs, and writes an answer citing **which file and page number** it came from.

### The 4 Core Building Blocks

| Step | Technical Term | Plain-English Meaning | Tool Used |
| :--- | :--- | :--- | :--- |
| **1** | **Chunking** | Read PDF text and slice long pages into small paragraphs (~1,000 characters). | `PyPDFLoader` & `RecursiveCharacterTextSplitter` |
| **2** | **Embeddings** | Convert each paragraph into numbers (vectors) capturing its **meaning**. | `OpenAIEmbeddings` (`text-embedding-3-small`) |
| **3** | **Vector Database** | Store all vectors in one searchable index for fast similarity search. | `FAISS` + `st.session_state` |
| **4** | **Grounded Answer** | Send top matching chunks (with **file name & page number**) to GPT. | `ChatOpenAI` (`gpt-4o-mini`) |"""),

    md_cell("""---
## Step 1: Install Required Libraries
We install the Python packages needed for the UI (`streamlit`), AI pipeline (`langchain`), PDF reading (`pypdf`), vector search (`faiss-cpu`), and API key loading (`python-dotenv`)."""),

    code_cell("!pip install -q streamlit langchain langchain-openai langchain-community langchain-text-splitters pypdf faiss-cpu python-dotenv"),

    md_cell("""---
## Step 2: Configure Your OpenAI API Key Safely
* Never hardcode API keys in your Python files. Store `OPENAI_API_KEY=sk-...` in a `.env` file instead.
* *(Skip running the cell below if you already added your real key to `.env` in VS Code.)*"""),

    code_cell("# Uncomment and run ONLY if you need to create a new .env file:\n# %%writefile .env\n# OPENAI_API_KEY=sk-proj-your-actual-key-here"),

    md_cell("""---
## Step 3: Build the Complete Web App (`rag_app.py`)
### Key Fresher Takeaways in This Code:
* **`%%writefile rag_app.py`**: Saves the entire cell into a standalone Python file that Streamlit can run.
* **`load_dotenv(override=True)`**: Loads your `.env` key and ignores any stale keys cached in Windows.
* **`st.session_state`**: Keeps your FAISS vector database in memory when you ask multiple questions.
* **1-Indexed Pages (`page + 1`)**: `PyPDFLoader` starts counting pages at `0`, so we add `1` for human-readable page numbers.
* **Disagreement Handling**: The system prompt instructs GPT to explicitly state when two PDFs disagree rather than silently picking one."""),

    code_cell(app_code),

    md_cell("""---
## Step 4: Launch the Streamlit App
1. Run the cell below (or run `streamlit run rag_app.py` in your terminal).
2. Open **`http://localhost:8501`** in your browser.
3. Upload multiple PDFs (`Ctrl + A` in your folder), click **Build Vector Store**, check the indexed chunk count, and ask questions!"""),

    code_cell("!streamlit run rag_app.py"),

    md_cell("""---
## 🎓 Step 5: Fresher Interview & Viva Cheat Sheet
* **Why use `chunk_overlap` (150 chars)?** So sentences aren't sliced cleanly in half at chunk boundaries, preserving context between neighboring chunks.
* **If one simple question cites 5 different pages, what is wrong?** Your `chunk_size` is likely too small (fragmenting one idea across many chunks) or `k=5` is pulling loosely related noise.
* **How does the app handle conflicting PDFs?** Every chunk is tagged `[File: name, Page: number]` before entering the prompt, and the system prompt forces the LLM to present both conflicting viewpoints with citations.""")
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.3"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open("multi_pdf_rag_app_fresher_guide.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print("SUCCESS! Created multi_pdf_rag_app_fresher_guide.ipynb")