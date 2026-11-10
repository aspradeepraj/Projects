import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Set up the webpage structure
st.set_page_config(page_title="Qwen 0.5B Chatbot", page_icon="🤖")
st.title("🤖 Qwen 2.5 0.5B Chatbot")
st.write("Type your question below to chat with the locally running model.")

# Use st.cache_resource so the model only loads ONCE into memory when the app starts
@st.cache_resource
def load_model():
    model_path = "Qwen/Qwen2.5-0.5B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        device_map="auto"
    )
    return tokenizer, model

# Load the model and tokenizer
with st.spinner("Loading model into memory... This may take a moment on the first run."):
    tokenizer, model = load_model()

# Create a clean text input block for user prompts
prompt = st.text_input("What do you want to ask the model?", placeholder="Type your prompt here...")

# Run generation only if the user has typed something
if prompt:
    with st.spinner("Generating response..."):
        # Format the input for the chat model
        messages = [
            {"role": "user", "content": prompt}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # Generate the tokens
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512
        )

        # Trim out the prompt tokens from the output IDs
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # Decode the final text answer
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
    # Display the final output inside a styled UI container block
    st.subheader("Response:")
    st.info(response)