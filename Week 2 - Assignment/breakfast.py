"""
===========================================================================
FILE: breakfast.py
ASSIGNMENT: Ask LangChain for 5 Breakfast Ideas

PREREQUISITES (Run once in your terminal before executing this script):
    pip install langchain langchain-openai langchain-core python-dotenv

    * langchain-core   -> Provides base interfaces, prompts, and message structures.
    * langchain-openai -> The specific bridge package to talk to OpenAI's servers.
    * python-dotenv    -> Safely loads secret API keys from a local .env file.
===========================================================================
"""

# =========================================================================
# 1. IMPORTS
# =========================================================================
# WHAT: Brings Python's 'os'/'sys' modules, 'load_dotenv', and LangChain's 'ChatOpenAI' into the script.
# WHY:  - 'ChatOpenAI' acts as a clean, standardized wrapper around OpenAI's raw HTTP API,
#         saving us from writing complex networking requests.
#       - 'load_dotenv' and 'os' let us read the secret API key from an environment variable
#         so we NEVER hard-code sensitive credentials in our script.
import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# =========================================================================
# 2. API KEY CONFIGURATION (Never Hard-Coded)
# =========================================================================
# WHAT: Loads environment variables from a '.env' file (if present) into the system runtime.
# WHY:  OpenAI requires authentication to verify your account and track usage.
#       ChatOpenAI is programmed to automatically search your system environment for
#       a variable named "OPENAI_API_KEY".
#       (Note: If you set $env:OPENAI_API_KEY in PowerShell or export it in Bash,
#       ChatOpenAI will still find it even without a .env file.)
load_dotenv()


def main():
    # Safety check to ensure the API key exists before calling OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Set it in your terminal or .env file.")
        sys.exit(1)

    # =====================================================================
    # 3. INITIALIZING THE MODEL
    # =====================================================================
    # WHAT: Creates an active AI model object named 'llm' configured with specific rules.
    # WHY:  - model="gpt-4o-mini" -> Chosen because it is fast, low-cost, and capable enough
    #                                for everyday text generation tasks.
    #       - temperature         -> Controls randomness/creativity (default is ~0.7).
    #                                Because it is not 0, running this script twice will
    #                                produce slightly different breakfast ideas each time.
    #                                (Tip: Set temperature=0 if you want the exact same 5 ideas every run.)
    llm = ChatOpenAI(model="gpt-4o-mini")

    # =====================================================================
    # 4. PINNING THE PROMPT FORMAT
    # =====================================================================
    # WHAT: Defines the exact instructions and formatting constraints sent to the model.
    # WHY:  A vague ask ("give me breakfast ideas") produces messy paragraphs or conversational filler.
    #       Pinning the format ensures we get strictly 5 items, numbered, one line each, with no preamble.
    #       (Note: We left "healthy" open for the model to decide, rather than restricting calories/macros.)
    prompt = (
        "List exactly 5 healthy breakfast ideas. "
        "Format them as a numbered list from 1 to 5, strictly one line each, "
        "with no intro, preamble, or extra commentary."
    )

    # =====================================================================
    # 5. INVOKING THE MODEL & EXTRACTING THE TEXT
    # =====================================================================
    # WHAT: Sends the prompt to OpenAI via llm.invoke() and prints ONLY reply.content.
    # WHY:  llm.invoke() returns an 'AIMessage' object packed with metadata (token counts,
    #       model name, response IDs)—NOT a plain string.
    #       Accessing '.content' extracts just the clean text string we actually want.
    reply = llm.invoke(prompt)

    # Uncomment the line below once if you want to inspect the full AIMessage object:
    # print(reply)

    print(reply.content)


# =========================================================================
# 6. CLEAN EXECUTION ENTRY POINT
# =========================================================================
# WHAT: Runs main() safely and catches Ctrl+C interrupts without red traceback errors.
# WHY:  Keeps terminal output clean if you stop the script early during execution.
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
        sys.exit(0)
