from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

prompts = [
    "Give me a one-sentence definition of an API.",
    "List 3 key differences between SQL and NoSQL databases with a brief explanation for each.",
    "Write a detailed, step-by-step guide on how a beginner can deploy a Python web app to the cloud, including best practices for security and environment variables."
]

for i, prompt in enumerate(prompts, start=1):
    print(f"--- Prompt {i} ---")
    print(llm.invoke(prompt).content)
    print("\n")
