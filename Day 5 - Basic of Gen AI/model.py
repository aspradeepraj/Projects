from transformers import AutoModelForCausalLM, AutoTokenizer

# Bypass the local folder and use the official Hugging Face repository ID directly
model_path = "Qwen/Qwen2.5-0.5B-Instruct"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("Loading model (this might take a minute on the first run)...")
model = AutoModelForCausalLM.from_pretrained(
    model_path, 
    device_map="auto"
)

print("\nModel loaded successfully! Type 'exit' or 'quit' to stop.\n")

# Start an interactive loop to ask you what you need
while True:
    prompt = input("What do you want to ask the model? >> ")
    
    # Check if you want to exit the script
    if prompt.strip().lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
        
    if not prompt.strip():
        continue

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

    print("\nGenerating output...")
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print("\n--- Model Response ---")
    print(response)
    print("-" * 22 + "\n")