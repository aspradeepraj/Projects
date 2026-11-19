import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load environment variables & initialize client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Extract: Load and read the raw CSV file
df = pd.read_csv("student_enrollment_raw.csv")
cleaned_rows = []

# 3. Transform: Loop through all 50 rows and clean via LLM
for index, row in df.iterrows():
    row_dict = row.fillna("").to_dict()
    
    prompt = f"""
    Clean this student enrollment row and return ONLY a raw JSON object. No markdown.
    Row data: {json.dumps(row_dict)}

    Rules:
    - Student_ID: keep as is
    - Name: Title Case (Manoj K)
    - Email: if invalid set INVALID_EMAIL
    - Phone: if less than 10 digits set MISSING
    - Course: only Python or Machine Learning or Data Science
    - Fee_Paid: yes/YES = true, no/NO = false
    - City: Title Case, empty = UNKNOWN
    - Enrolled_Date: convert to YYYY-MM-DD
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    cleaned_record = json.loads(response.choices[0].message.content)
    cleaned_rows.append(cleaned_record)
    print(f"Cleaned row {index + 1}/{len(df)}")

# 4. Load: Save the cleaned records to a new CSV file
cleaned_df = pd.DataFrame(cleaned_rows)
cleaned_df.to_csv("students_cleaned.csv", index=False)
print("ETL complete! Saved to students_cleaned.csv")