from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 1. Load your API key from the .env file
load_dotenv()

# 2. Initialize the Model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 3. Define the Prompt Template
# We define a "system" message to give the AI a persona, and a "user" message for the input.
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert chef. Create a quick, 3-step recipe using the ingredient provided by the user."),
    ("user", "I want to cook something using: {ingredient}")
])

# 4. Format the prompt with a real ingredient to see how it looks
formatted_prompt = prompt_template.format_messages(ingredient="Eggs")
print("--- Formatted Prompt Look ---")
print(formatted_prompt)