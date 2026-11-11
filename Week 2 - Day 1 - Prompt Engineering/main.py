import ollama
from pathlib import Path
from datetime import datetime

# Model configuration
MODEL = "qwen2.5:7b"

# Load the master prompt
prompt_file = Path(__file__).parent / "meal_plan_prompt.md"

if not prompt_file.exists():
    print("Master prompt file not found!")
    exit()

with open(prompt_file, "r", encoding="utf-8") as file:
    system_prompt = file.read()

# Initialize conversation
messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]

print("\n========================================")
print(" SOUTH INDIAN MEAL PLANNER")
print(" Powered by Ollama + Qwen (Streaming)")
print("========================================")

print("\nStarting meal planner...\n")

# Ask AI to collect user variables
messages.append({
    "role": "user",
    "content": "Start the meal planner. First collect and validate my current user variables according to your instructions. Do not generate the meal plan until the required details are available."
})

try:
    # Initial dynamic greeting with streaming
    response_stream = ollama.chat(
        model=MODEL,
        messages=messages,
        stream=True
    )

    print("AI: ", end="", flush=True)
    answer = ""
    for chunk in response_stream:
        token = chunk['message']['content']
        print(token, end="", flush=True)
        answer += token
    print() # Break line after stream finishes

    messages.append({
        "role": "assistant",
        "content": answer
    })

except Exception as e:
    print("Ollama connection error:", e)
    exit()

# Interactive conversation loop
while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() == "exit":
        print("Thank you for using the Meal Planner!")
        break

    # Reset for a new user session
    if user_input.lower() == "reset":
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        print("\nStarting a fresh user session...")
        user_input = (
            "Start a new meal planning session. "
            "Collect all current user variables again. "
            "Do not reuse previous user information."
        )

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:
        # Dynamic processing with options and streaming enabled
        response_stream = ollama.chat(
            model=MODEL,
            messages=messages,
            options={
                "temperature": 0.4
            },
            stream=True
        )

        print("\nAI:\n")
        answer = ""
        for chunk in response_stream:
            token = chunk['message']['content']
            print(token, end="", flush=True)
            answer += token
        print() # Break line after stream finishes

        messages.append({
            "role": "assistant",
            "content": answer
        })

        # Save generated meal plan safely using pathlib paths
        if "day 1" in answer.lower() and "day 7" in answer.lower():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Meal_Plan_{timestamp}.md"
            output_file = prompt_file.parent / output_filename

            with open(output_file, "w", encoding="utf-8") as file:
                file.write(answer)

            print(f"\n[Success] Meal plan saved to: {output_file.resolve()}")

    except Exception as e:
        print("\nError encountered during streaming context:", e)