import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def query_networkx_graph(nx_graph, query_entity):
    """Traverse NetworkX graph to extract neighborhood context for a given entity"""
    graph = nx_graph._graph
    
    # Find matching nodes (case-insensitive partial match)
    matching_nodes = [node for node in graph.nodes if query_entity.lower() in node.lower()]
    
    context_lines = []
    for node in matching_nodes:
        # Outgoing edges
        for _, target, data in graph.out_edges(node, data=True):
            context_lines.append(f"{node} --[{data.get('relation', 'RELATED_TO')}]--> {target}")
        # Incoming edges
        for source, _, data in graph.in_edges(node, data=True):
            context_lines.append(f"{source} --[{data.get('relation', 'RELATED_TO')}]--> {node}")
            
    return "\n".join(context_lines)

# Example usage combined with LLM generation:
load_dotenv()
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant. Answer the user's question accurately using ONLY the provided Knowledge Graph context below.\n\nContext:\n{context}"),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()

# (Assuming `nx_graph` is already populated from your previous NetworkX script)
# user_question = "What is Pradeepraj building?"
# graph_context = query_networkx_graph(nx_graph, "Pradeepraj")
# response = chain.invoke({"context": graph_context, "question": user_question})
# print(response)