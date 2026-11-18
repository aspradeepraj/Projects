import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

# Load environment variables
load_dotenv()

# 1. Connect to Neo4j AuraDB
db = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# 2. Initialize the LLM
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# 3. Create the Graph Cypher QA Chain
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=db,
    verbose=True,
    allow_dangerous_requests=True  # Required for executing generated Cypher queries
)

# 4. Ask a question against your Knowledge Graph
response = chain.invoke({"query": "What application is Pradeepraj building and what tools does it use?"})

print("\n--- Graph RAG Response ---")
print(response["result"])