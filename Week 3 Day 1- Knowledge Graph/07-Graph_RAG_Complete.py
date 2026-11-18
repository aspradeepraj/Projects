import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

# 1. Load environment variables (OPENAI_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
load_dotenv()

def run_knowledge_graph_pipeline(file_path: str, user_question: str):
    print("--- Step 1: Loading & Splitting Documents ---")
    loader = TextLoader(file_path)
    raw_documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50
    )
    documents = text_splitter.split_documents(raw_documents)
    print(f"Total chunks created: {len(documents)}")

    print("\n--- Step 2: Entity & Relationship Extraction ---")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    graph_transformer = LLMGraphTransformer(llm=llm)
    
    graph_documents = graph_transformer.convert_to_graph_documents(documents)
    print(f"Extracted graph documents from {len(documents)} chunks.")

    print("\n--- Step 3: Storing in Neo4j AuraDB ---")
    db = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    # Add extracted graph elements into Neo4j
    db.add_graph_documents(graph_documents, include_source=True)
    print("-> Graph successfully stored in Neo4j AuraDB!")

    print(f"\n--- Step 4: Graph Query / RAG Retrieval ---")
    print(f"Question: '{user_question}'")
    
    # Initialize the Text-to-Cypher QA Chain
    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=db,
        verbose=True,
        allow_dangerous_requests=True
    )

    response = chain.invoke({"query": user_question})
    
    print("\n==============================")
    print("FINAL GRAPH RAG ANSWER:")
    print("==============================")
    print(response["result"])

if __name__ == "__main__":
    # Define your input text file and the question you want to ask the graph
    target_file = "sample.txt"
    sample_query = "Whatis Python?"
    
    run_knowledge_graph_pipeline(target_file, sample_query)