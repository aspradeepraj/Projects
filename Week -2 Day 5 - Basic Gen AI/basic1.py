from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 1. Load API Key from .env & Initialize Model
load_dotenv(override=True)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. Define the Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert chef. Create a quick, 3-step recipe using the ingredient provided by the user."),
    ("user", "I want to cook something using: {ingredient}")
])

# 3. Create the Chain using LCEL (|)
chain = prompt_template | llm

# 4. Run (Invoke) the chain
print("Sending request to AI Chef...\n")
response = chain.invoke({"ingredient": "Eggs"})

print("--- AI Response ---")
print(response.content)