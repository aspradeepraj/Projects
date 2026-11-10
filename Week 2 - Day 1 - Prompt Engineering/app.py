import ollama
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="South Indian Weight-Loss Meal Planner",
    page_icon="🥗",
    layout="wide",
)

st.title("🥗 Dynamic South Indian Vegetarian Weight-Loss Meal Planner")
st.markdown(
    "Powered by **Streamlit** and **Ollama (Local LLM)**. Enter your profile"
    " details below to generate your custom, calorie-controlled 7-day meal"
    " plan."
)

# Input Form
with st.form("meal_planner_form"):
  st.subheader("📋 Your Profile & Preferences")

  col1, col2, col3 = st.columns(3)

  with col1:
    age = st.number_input("Age (years)", min_value=15, max_value=100, value=42)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
    height = st.number_input(
        "Height (cm)", min_value=100, max_value=220, value=173
    )

  with col2:
    current_weight = st.number_input(
        "Current Weight (kg)", min_value=30.0, max_value=250.0, value=92.0
    )
    target_weight = st.number_input(
        "Target Weight (kg)", min_value=30.0, max_value=250.0, value=75.0
    )
    activity_level = st.selectbox(
        "Activity Level",
        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"],
        index=1,
    )

  with col3:
    dietary_restrictions = st.selectbox(
        "Dietary Restrictions", ["Vegetarian", "Vegan", "Eggless", "Other"], index=0
    )
    cuisine_pref = st.selectbox(
        "Cuisine Preference",
        [
            "Mixed South Indian",
            "Tamil Nadu",
            "Karnataka",
            "Andhra Pradesh",
            "Kerala",
        ],
        index=0,
    )
    meals_per_day = st.text_input("Meals Per Day", value="3 main meals + 1 snack")

  col4, col5 = st.columns(2)
  with col4:
    food_budget = st.selectbox(
        "Food Budget", ["Affordable", "Moderate", "Flexible"], index=0
    )
    cooking_pref = st.selectbox(
        "Cooking Preference",
        ["Simple", "Traditional", "Quick preparation", "Flexible"],
        index=0,
    )

  with col5:
    allergies = st.text_input(
        "Allergies & Food Dislikes", value="No allergies / None"
    )
    health_considerations = st.text_input(
        "Health Considerations", value="None"
    )

  submitted = st.form_submit_button(
      "Generate Custom 7-Day Meal Plan 🚀", type="primary"
  )

# Generation Logic
if submitted:
  system_prompt = (
      "Act as an experienced Indian Clinical Dietitian and Nutritionist"
      " specializing in South Indian vegetarian nutrition, sustainable weight"
      " management, calorie-controlled meal planning, and protein/fibre"
      " optimization. Provide a comprehensive 7-day meal plan with daily"
      " calorie/protein breakdowns, a categorized weekly grocery list, and"
      " practical meal prep tips."
  )

  user_prompt = f"""
    Please generate a personalized 7-day South Indian vegetarian weight-loss meal plan based on these user details:
    - Age: {age} years
    - Gender: {gender}
    - Height: {height} cm
    - Current Weight: {current_weight} kg
    - Target Weight: {target_weight} kg
    - Activity Level: {activity_level}
    - Dietary Restrictions: {dietary_restrictions}
    - Cuisine Preference: {cuisine_pref}
    - Meals Per Day: {meals_per_day}
    - Food Budget: {food_budget}
    - Cooking Preference: {cooking_pref}
    - Allergies & Food Dislikes: {allergies}
    - Health Considerations: {health_considerations}
    
    Please format the response clearly with:
    1. User Nutrition Overview (Maintenance calories, recommended calorie target, protein target).
    2. 7-Day Meal Plan (Day 1 through Day 7 with tables/breakdowns showing Dish Name, Portion Size, Calories, and Nutritional Focus).
    3. Weekly Grocery List.
    4. Meal Preparation Tips.
    5. Lifestyle Recommendations.
    """

  with st.spinner(
      "🤖 Ollama is calculating your nutritional targets and crafting your"
      " custom meal plan..."
  ):
    try:
      # Calls the local Ollama instance
      response = ollama.chat(
          model="llama3",  # Change to your installed model if needed (e.g., 'gemma2', 'mistral')
          messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt},
          ],
      )

      st.success("✨ Your personalized meal plan is ready!")
      st.markdown("---")
      st.markdown(response["message"]["content"])

    except Exception as e:
      st.error(
          f"⚠️ Error communicating with Ollama: {e}\n\nMake sure Ollama is"
          " running in the background (`ollama serve`) and you have pulled a"
          " model using `ollama pull llama3`."
      )