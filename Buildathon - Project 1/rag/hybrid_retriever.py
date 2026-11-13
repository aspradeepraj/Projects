import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from sentence_transformers import CrossEncoder

load_dotenv()

class HybridGovernanceRAG:
    def __init__(self, pdf_path: str = "data/sow_contract.pdf"):
        self.embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
        self.llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0)
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.chunks = self._load_and_split(pdf_path)
        self.ensemble_retriever = self._build_hybrid_retriever()

    def _load_and_split(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            # Fallback synthetic contract clauses for immediate MVP testing
            from langchain_core.documents import Document

            return [
                Document(page_content="Clause 4.2 Scope & Change Control: Any scope addition exceeding 5% of baseline story points requires a signed Change Request (CR) prior to sprint execution.", metadata={"source": "SOW_v2.pdf", "page": 4}),
                Document(page_content="Clause 7.1 Budget Burn Threshold: If cumulative budget burn exceeds 80% before Milestone 3 completion, an immediate Executive Steering Escalation is mandatory.", metadata={"source": "SOW_v2.pdf", "page": 9}),
                Document(page_content="Clause 9.4 SLA & Velocity: Sprint velocity variance greater than 20% over two consecutive sprints triggers a formal Delivery Recovery Plan.", metadata={"source": "SOW_v2.pdf", "page": 12})
            ]
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
        return splitter.split_documents(docs)

    def _build_hybrid_retriever(self):
        # 1. Sparse Keyword Retriever (BM25)
        bm25 = BM25Retriever.from_documents(self.chunks)
        bm25.k = 4

        # 2. Dense Vector Retriever (Chroma)
        vectorstore = Chroma.from_documents(self.chunks, self.embeddings)
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        # 3. Hybrid Ensemble (50% Keyword / 50% Semantic)
        return EnsembleRetriever(retrievers=[bm25, vector_retriever], weights=[0.5, 0.5])

    def retrieve_and_rerank(self, query: str, top_k: int = 3):
        # Step 1: Hybrid Retrieval
        raw_docs = self.ensemble_retriever.invoke(query)
        
        # Step 2: Cross-Encoder Re-Ranking
        pairs = [[query, doc.page_content] for doc in raw_docs]
        scores = self.reranker.predict(pairs)
        scored_docs = sorted(zip(scores, raw_docs), key=lambda x: x[0], reverse=True)
        
        # Step 3: Self-RAG Relevance Gate (Filter low-confidence noise)
        verified_docs = [doc for score, doc in scored_docs[:top_k] if score > -2.0]
        return verified_docs