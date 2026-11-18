import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs import NetworkXGraph

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

# 3. Initialize NetworkX Graph in-memory
nx_graph = NetworkXGraph()

# 4. Add the extracted graph documents into NetworkX
print("Saving graph documents to NetworkX in-memory graph...")
nx_graph.add_graph_documents(graph_documents)

# 5. Inspect the local graph nodes and edges
print("\n-> Step 3 (NetworkX) Complete!")
print(f"Total Nodes in Memory: {len(nx_graph._graph.nodes)}")
print(f"Total Edges in Memory: {len(nx_graph._graph.edges)}")

print("\nNodes:")
for node, data in nx_graph._graph.nodes(data=True):
    print(f"  - {node}: {data}")

print("\nEdges / Relationships:")
for u, v, data in nx_graph._graph.edges(data=True):
    print(f"  - {u} -> {v} | Data: {data}")