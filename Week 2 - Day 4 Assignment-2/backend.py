import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

app = FastAPI(title="PDF FAISS RAG Backend")

# Configuration
FAISS_INDEX_PATH = "faiss_index"
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# Initialize Embedding Model (runs locally)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


# ==========================================
# PIPELINE 1: Load -> Split -> Embed -> Save
# ==========================================
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)

    try:
        # 1. Save uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Data Load
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        # 3. Text Split
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

        # 4. Embedding & Save to FAISS File
        if os.path.exists(FAISS_INDEX_PATH):
            # Load existing index and merge new vectors
            vector_db = FAISS.load_local(
                FAISS_INDEX_PATH, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            vector_db.add_documents(chunks)
        else:
            # Create a new FAISS index
            vector_db = FAISS.from_documents(chunks, embeddings)

        # Persist FAISS index locally
        vector_db.save_local(FAISS_INDEX_PATH)

        return {
            "status": "success",
            "filename": file.filename,
            "chunks_added": len(chunks),
            "message": "PDF processed and stored in FAISS index successfully."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary PDF file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# ==========================================
# PIPELINE 2: Fetch from FAISS & Return
# ==========================================
@app.post("/search")
async def search_vector_db(request: QueryRequest):
    if not os.path.exists(FAISS_INDEX_PATH):
        raise HTTPException(
            status_code=404, 
            detail="FAISS index not found. Please upload a PDF first."
        )

    try:
        # 1. Load FAISS index from file
        vector_db = FAISS.load_local(
            FAISS_INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )

        # 2. Perform similarity search with relevance scores
        results = vector_db.similarity_search_with_score(request.query, k=request.top_k)

        # 3. Format results for display
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "distance_score": float(score)  # Lower score = closer match in L2 distance
            })

        return {
            "query": request.query,
            "results": formatted_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))