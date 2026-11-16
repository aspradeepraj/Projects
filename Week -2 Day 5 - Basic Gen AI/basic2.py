from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# Import the string output parser
from langchain_core.output_parsers import StrOutputParser

# 1. Load API Key from .env & Initialize Model
load_dotenv(override=True)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. Define the Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert chef. Create a quick, 3-step recipe using the ingredient provided by the user."),
    ("user", "I want to cook something using: {ingredient}")
])

# 3. Create the Chain with the Output Parser added to the end
# The output parser will catch the AIMessage and strip away everything except the text.
chain = prompt_template | llm | StrOutputParser()

# 4. Run the chain
print("Sending request to AI Chef...\n")
response = chain.invoke({"ingredient": "Eggs"})

print("--- Clean AI Response ---")
print(response)