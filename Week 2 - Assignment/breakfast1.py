import os
import sys
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load OPENAI_API_KEY from your .env file
load_dotenv()

# Page setup
st.set_page_config(page_title="Healthy Breakfast Generator", page_icon="🥣", layout="centered")
st.title("🥣 5 Healthy Breakfast Ideas")
st.caption("Powered by LangChain & OpenAI")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found! Please add it to your .env file.")
    st.stop()

# Sidebar control to test the assignment's temperature concept live!
temperature = st.sidebar.slider(
    "Model Temperature (Creativity)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="0.0 gives the exact same 5 ideas every click. Higher values give new ideas each time."
)

# Optional dietary preference input
preference = st.text_input("Any dietary preference? (Optional)", placeholder="e.g., vegetarian, high-protein, South Indian")

# Button to generate ideas
if st.button("Generate 5 Breakfast Ideas", type="primary"):
    with st.spinner("Cooking up ideas..."):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)

        extra_filter = f" that are {preference}" if preference else ""
        prompt = (
            f"List exactly 5 healthy breakfast ideas{extra_filter}. "
            "Format them as a numbered list from 1 to 5, strictly one line each, "
            "with no intro, preamble, or extra commentary."
        )

        reply = llm.invoke(prompt)
        st.markdown("### Your Breakfast Menu")
        st.markdown(reply.content)