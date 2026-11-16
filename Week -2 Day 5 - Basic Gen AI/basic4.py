from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. Setup
load_dotenv(override=True)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. Updated Prompt Template with a History Placeholder
# We must use MessagesPlaceholder so LangChain knows exactly where to inject the past chat history.
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert chef. Help the user with recipes and cooking advice based on their conversation history."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])

# 3. Build the Base Chain
base_chain = prompt_template | llm | StrOutputParser()

# 4. Manage Memory / Chat History Storage
# In a real app, this would be a database. For this basic app, we use a dictionary in memory.
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 5. Wrap the Chain with Message History
# This automatically feeds past messages into 'chat_history' and saves new ones.
conversational_chain = RunnableWithMessageHistory(
    base_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# 6. Create an Interactive Terminal Chat Loop
print("--- AI Chef Ready! (Type 'exit' or 'quit' to stop) ---\n")

# We give our conversation a unique session ID
config = {"configurable": {"session_id": "user_cooking_session"}}

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Chef: Happy cooking! Goodbye!")
        break
        
    print("Chef: ", end="", flush=True)
    
    # We call .stream() on the conversational chain
    for chunk in conversational_chain.stream({"input": user_input}, config=config):
        print(chunk, end="", flush=True)
    print("\n") # New line after streaming finishes