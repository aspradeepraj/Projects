import sys
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load environment variables from the .env file
load_dotenv()

# --- 1. Page Configuration & Setup ---
st.set_page_config(page_title="AI Chef Assistant", page_icon="🍳", layout="centered")
st.title("🍳 Your AI Chef Assistant")
st.caption("Ask for recipes, cooking tips, or modification ideas based on your history!")

# --- 2. Initialize LangChain Components ---
@st.cache_resource
def init_langchain():
    # ChatOpenAI automatically detects OPENAI_API_KEY from your .env file
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert chef. Help the user with recipes and cooking advice based on their conversation history."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    
    base_chain = prompt_template | llm | StrOutputParser()
    return base_chain

def get_session_history(session_id: str):
    return st.session_state.chat_history

def main():
    base_chain = init_langchain()

    # --- 3. Manage Memory using Streamlit Session State ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = InMemoryChatMessageHistory()

    conversational_chain = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    # --- 4. Render Chat History on UI ---
    for msg in st.session_state.chat_history.messages:
        role = "user" if msg.type == "human" else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    # --- 5. Handle New User Input ---
    if user_input := st.chat_input("What ingredients do you have?"):
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            config = {"configurable": {"session_id": "streamlit_session"}}
            st.write_stream(
                conversational_chain.stream({"input": user_input}, config=config)
            )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
        sys.exit(0)
