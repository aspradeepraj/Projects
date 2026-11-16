from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Setup
load_dotenv(override=True)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert chef. Create a quick, 3-step recipe using the ingredient provided by the user."),
    ("user", "I want to cook something using: {ingredient}")
])

chain = prompt_template | llm | StrOutputParser()

# 2. Stream the response instead of invoking it whole
print("AI Chef is thinking... \n")

# .stream() returns a generator that yields chunks of text as they arrive
for chunk in chain.stream({"ingredient": "Eggs"}):
    # print(..., end="", flush=True) ensures text prints side-by-side immediately
    print(chunk, end="", flush=True)

print("\n\n--- Finished Streaming ---")