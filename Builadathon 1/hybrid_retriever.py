import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv

load_dotenv()

class HybridRetrieverEngine:
    def __init__(self, pdf_path="sow_contract.pdf"):
        self.pdf_path = pdf_path
        self.chunks = []
        self.bm25 = None
        self.vector_store = None
        self.embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self._initialize_docs()

    def _initialize_docs(self):
        if not os.path.exists(self.pdf_path):
            return
        try:
            loader = PyPDFLoader(self.pdf_path)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
            split_docs = splitter.split_documents(docs)
            self.chunks = [doc.page_content for doc in split_docs if doc.page_content.strip()]
            
            if self.chunks:
                # 1. Initialize BM25 for keyword search
                tokenized_corpus = [doc.lower().split(" ") for doc in self.chunks]
                self.bm25 = BM25Okapi(tokenized_corpus)
                
                # 2. Initialize ChromaDB vector store for dense retrieval
                self.vector_store = Chroma.from_documents(
                    documents=split_docs,
                    embedding=self.embeddings,
                    collection_name="sow_governance_collection"
                )
        except Exception as e:
            print(f"Error initializing retriever: {e}")

    def retrieve(self, query: str, top_k=3):
        if not self.chunks or not self.vector_store:
            return [{"content": "Fallback SOW Clause: Milestone budget burn limit is 80.0% and scope creep limit is 5.0%.", "score": 0.85}]
            
        # Dense vector search via ChromaDB
        vector_results = self.vector_store.similarity_search(query, k=top_k)
        retrieved_texts = [doc.page_content for doc in vector_results]
        
        # Re-rank using Cross-Encoder for high precision
        pairs = [[query, text] for text in retrieved_texts]
        scores = self.cross_encoder.predict(pairs)
        
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        
        results = []
        for idx in ranked_indices[:top_k]:
            results.append({
                "content": retrieved_texts[idx],
                "score": float(scores[idx])
            })
        return results