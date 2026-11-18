import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

# Load environment variables (like OPENAI_API_KEY) from a .env file
load_dotenv()

# 1. Load the document
loader = TextLoader("sample.txt")
raw_documents = loader.load()

# 2. Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)
documents = text_splitter.split_documents(raw_documents)

# 3. Initialize the LLM for graph extraction
# (Ensure your OPENAI_API_KEY is set in your environment variables or .env)
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# 4. Initialize the LLMGraphTransformer
graph_transformer = LLMGraphTransformer(llm=llm)

# 5. Extract graph documents (nodes and edges) from our text chunks
print("Extracting entities and relationships...")
graph_documents = graph_transformer.convert_to_graph_documents(documents)

# 6. Inspect the extracted graph structure
for i, graph_doc in enumerate(graph_documents):
    print(f"\n--- Graph Elements from Chunk {i+1} ---")
    print("Nodes found:")
    for node in graph_doc.nodes:
        print(f"  - {node.id} ({node.type})")
    
    print("Relationships found:")
    for rel in graph_doc.relationships:
        print(f"  - {rel.source.id} --[:{rel.type}]-> {rel.target.id}")