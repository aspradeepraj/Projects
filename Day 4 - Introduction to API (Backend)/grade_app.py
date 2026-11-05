import streamlit as st


def get_letter_grade(mark: float) -> str:
    """Calculates letter grade based on the mark provided."""
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "F"


# Page Configuration
st.set_page_config(page_title="Student Grade Manager", page_icon="🎓", layout="wide")

# Initialize session state for persistent storage across reruns
if "students" not in st.session_state:
    st.session_state.students = []

st.title("🎓 Student Grade Manager")

# Sidebar form to add student
with st.sidebar:
    st.header("Add Student")
    with st.form("add_student_form", clear_on_submit=True):
        name = st.text_input("Name")
        mark = st.number_input(
            "Mark (0 to 100)", min_value=0.0, max_value=100.0, step=1.0
        )
        submitted = st.form_submit_button("Add Student")

        if submitted:
            cleaned_name = name.strip()
            if not cleaned_name:
                st.error("Please enter a valid student name.")
            else:
                grade = get_letter_grade(mark)
                st.session_state.students.append(
                    {"Name": cleaned_name, "Mark": mark, "Grade": grade}
                )
                st.success(f"Added {cleaned_name} with mark {mark} ({grade}).")

# Main Section
if st.session_state.students:
    # Calculate metrics
    marks = [s["Mark"] for s in st.session_state.students]
    avg_mark = sum(marks) / len(marks)
    max_mark = max(marks)
    min_mark = min(marks)

    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", len(st.session_state.students))
    col2.metric("Class Average", f"{avg_mark:.1f}")
    col3.metric("Highest Mark", f"{max_mark:.1f}")
    col4.metric("Lowest Mark", f"{min_mark:.1f}")

    st.divider()

    # Results Table
    st.subheader("Student Results")
    st.dataframe(
        st.session_state.students, use_container_width=True, hide_index=True
    )
else:
    st.info("No student records available. Use the sidebar form to add students.")