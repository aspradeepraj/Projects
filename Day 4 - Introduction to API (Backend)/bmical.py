import streamlit as st

# Sets up the primary page layout header banner at the top of the browser window.
st.title(" Personal BMI Calculator")
st.write("Calculate your Body Mass Index (BMI) instantly based on your metrics.")

# Creates a horizontal row of columns to layout inputs side-by-side cleanly.
col1, col2 = st.columns(2)

with col1:
    # Captures the user's weight in kilograms using a numeric precision stepper.
    weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1)

with col2:
    # Captures the user's height in centimeters using a numeric precision stepper.
    height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)

# Renders a central visual button control layout on the page canvas.
if st.button("Calculate BMI"):
    # Converts the raw centimeter height value into meters to match standard mathematical formulas.
    height_m = height_cm / 100
    
    # Calculates the final metric BMI scale by dividing weight by height squared.
    bmi = weight / (height_m ** 2)
    
    # Displays the computed index score rounded neatly to two decimal places.
    st.subheader(f"Your BMI is: {bmi:.2f}")
    
    # Conditional control flows mapping the score value to standard health categories.
    if bmi < 18.5:
        # Renders an orange feedback warning alert window for underweight conditions.
        st.warning("Category: Underweight")
        st.write("Consider consulting a healthcare provider or nutritionist for advice.")
    elif 18.5 <= bmi < 25.0:
        # Renders a green success validation alert window for ideal weight conditions.
        st.success("Category: Normal weight")
        st.write("Great job! Keep maintaining a balanced diet and regular physical activity.")
    elif 25.0 <= bmi < 30.0:
        # Renders an orange feedback warning alert window for overweight conditions.
        st.warning("Category: Overweight")
        st.write("Adopting a balanced routine of physical exercise and portion tracking can help.")
    else:
        # Renders a red error panic alert window highlighting high-risk conditions.
        st.error("Category: Obesity")
        st.write("We highly recommend speaking with a medical practitioner to coordinate safe long-term targets.")