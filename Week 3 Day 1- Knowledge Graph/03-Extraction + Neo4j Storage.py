import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph

# Load environment variables
load_dotenv()

# 1. Load and split the document
loader = TextLoader("sample.txt")
raw_documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)
documents = text_splitter.split_documents(raw_documents)

# 2. Initialize LLM and Graph Transformer
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
graph_transformer = LLMGraphTransformer(llm=llm)

print("Extracting entities and relationships...")
graph_documents = graph_transformer.convert_to_graph_documents(documents)

# 3. Connect to Neo4j AuraDB
# Make sure your .env has NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD set correctly
db = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# 4. Add the extracted graph documents into Neo4j AuraDB
print("Saving graph documents to Neo4j AuraDB...")
db.add_graph_documents(graph_documents, include_source=True)

print("-> Step 3 Complete: Graph successfully stored in Neo4j AuraDB!")