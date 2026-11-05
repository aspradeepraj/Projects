import streamlit as st


def get_letter_grade(mark: float) -> str:
    """Returns letter grade based on standard grading scale."""
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


# Initialize session state for student list if it doesn't exist yet
if "students" not in st.session_state:
    st.session_state.students = []

st.set_page_config(page_title="Grade Manager", page_icon="🎓", layout="wide")
st.title("🎓 Student Grade Manager")

# Sidebar/Form to Add Student
with st.sidebar:
    st.header("Add New Student")
    with st.form(key="add_student_form", clear_on_submit=True):
        name = st.text_input("Student Name")
        mark = st.number_input(
            "Mark (0 - 100)", min_value=0.0, max_value=100.0, step=1.0
        )
        submit = st.form_submit_button("Add Student")

        if submit:
            if not name.strip():
                st.error("Please enter a valid student name.")
            else:
                grade = get_letter_grade(mark)
                st.session_state.students.append(
                    {"Name": name.strip(), "Mark": mark, "Grade": grade}
                )
                st.success(f"Added {name.strip()} with mark {mark} ({grade}).")

# Main Dashboard Content
if not st.session_state.students:
    st.info("No students added yet. Use the sidebar form to add students.")
else:
    # Calculations
    marks = [s["Mark"] for s in st.session_state.students]
    avg_mark = sum(marks) / len(marks)
    max_mark = max(marks)
    min_mark = min(marks)

    # Class Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", len(st.session_state.students))
    col2.metric("Class Average", f"{avg_mark:.2f}")
    col3.metric("Highest Mark", f"{max_mark:.2f}")
    col4.metric("Lowest Mark", f"{min_mark:.2f}")

    st.divider()

    # Results Table
    st.subheader("Student Results")
    st.dataframe(
        st.session_state.students,
        use_container_width=True,
        hide_index=True,
    )

    # Optional reset button
    if st.button("Clear All Records"):
        st.session_state.students = []
        st.rerun()