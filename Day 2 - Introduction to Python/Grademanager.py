
# Import required modules
import os
import glob
from datetime import datetime
from openpyxl import Workbook, load_workbook

# List of subjects
subjects = ["English", "Language", "Maths", "Science"]

# Dictionary to store student records
students = {}

# Get the folder where this Python program is saved
folder_path = os.path.dirname(os.path.abspath(__file__))

# Get the current date and time for the Excel filename
date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create the Excel filename
data_file = os.path.join(folder_path, "Student data_" + date_time + ".xlsx")


# FUNCTION 1: LOAD STUDENTS
# Load previously saved student records from the latest Excel file
def load_students():

    # Find all previously created Student data Excel files
    files = glob.glob(os.path.join(folder_path, "Student data_*.xlsx"))

    # Check whether any previous Excel file exists
    if len(files) == 0:
        print("No previous records found.")
        return {}

    try:
        # Get the latest Excel file based on its modified time
        latest_file = max(files, key=os.path.getmtime)

        # Open the latest Excel file
        workbook = load_workbook(latest_file)

        # Select the active worksheet
        sheet = workbook.active

        # Read student records starting from row 2
        for row in sheet.iter_rows(min_row=2, values_only=True):

            # Check that the row contains student data
            if row[0] is not None:

                name = row[0]

                # Read subject marks
                marks = {}

                for index in range(len(subjects)):
                    marks[subjects[index]] = row[index + 1]

                # Store student details in the dictionary
                students[name] = {
                    "marks": marks,
                    "total": row[5],
                    "average": row[6],
                    "grade": row[7]
                }

        # Close the Excel file
        workbook.close()

        print("Previous student records loaded successfully.")

        return students

    except (OSError, ValueError, TypeError, IndexError):
        print("Unable to read previous Excel records.")
        return {}


# FUNCTION 2: SAVE STUDENTS
# Save all student records into an Excel workbook
def save_students():

    try:
        # Create a new Excel workbook
        workbook = Workbook()

        # Select the active worksheet
        sheet = workbook.active

        # Give a name to the worksheet
        sheet.title = "Student Records"

        # Add column headings
        headers = [
            "Student Name",
            "English",
            "Language",
            "Maths",
            "Science",
            "Total",
            "Average",
            "Grade"
        ]

        sheet.append(headers)

        # Add each student's details into Excel
        for name in students:

            details = students[name]

            row = [
                name,
                details["marks"]["English"],
                details["marks"]["Language"],
                details["marks"]["Maths"],
                details["marks"]["Science"],
                details["total"],
                details["average"],
                details["grade"]
            ]

            sheet.append(row)

        # Adjust column widths for readability
        for column in sheet.columns:
            column_letter = column[0].column_letter
            sheet.column_dimensions[column_letter].width = 18

        # Save the Excel file
        workbook.save(data_file)

        # Close the workbook
        workbook.close()

        print("Student records saved in Excel successfully.")

    except (OSError, PermissionError):
        print("Unable to save Excel file. Close it if it is already open.")


# FUNCTION 3: CALCULATE GRADE
# Calculate the grade based on average marks
def calculate_grade(average):

    if average >= 90:
        return "A+"

    elif average >= 80:
        return "A"

    elif average >= 70:
        return "B"

    elif average >= 60:
        return "C"

    elif average >= 50:
        return "D"

    else:
        return "F"


# FUNCTION 4: ADD STUDENT
# Collect student details and save the student record
def add_student():

    student_name = input("Enter student name: ").strip()

    # Check whether the name is empty
    if student_name == "":
        print("Student name cannot be empty.")
        return

    # Check whether the student already exists
    for name in students:

        if name.lower() == student_name.lower():
            print("Student already exists.")
            return

    # Create a dictionary to store subject marks
    marks = {}

    # Get marks for each subject
    for subject in subjects:

        while True:

            try:
                mark = int(input("Enter marks for " + subject + ": "))

                # Check whether marks are between 0 and 100
                if mark >= 0 and mark <= 100:
                    marks[subject] = mark
                    break

                else:
                    print("Marks must be between 0 and 100.")

            except ValueError:
                print("Please enter numbers only.")

    # Calculate total marks
    total = 0

    for subject in subjects:
        total = total + marks[subject]

    # Calculate average marks
    average = total / len(subjects)

    # Calculate grade
    grade = calculate_grade(average)

    # Store student details
    students[student_name] = {
        "marks": marks,
        "total": total,
        "average": average,
        "grade": grade
    }

    print("Student added successfully.")

    # Save all student records into Excel
    save_students()


# FUNCTION 5: DISPLAY ONE STUDENT
# Display the report of an individual student
def display_student(name, details):

    print("\nStudent Name:", name)

    # Display subject marks
    for subject in subjects:
        print(subject + ":", details["marks"][subject])

    print("Total Marks:", details["total"], "/", len(subjects) * 100)
    print("Average:", round(details["average"], 2))
    print("Grade:", details["grade"])
    print("-----------------------------")


# FUNCTION 6: DISPLAY ALL STUDENTS
# Display reports of all students
def display_students():

    if len(students) == 0:
        print("No student records available.")

    else:
        for name in students:
            display_student(name, students[name])


# FUNCTION 7: DISPLAY CLASS SUMMARY
# Calculate and display overall class performance
def display_class_summary():

    if len(students) == 0:
        print("No student records available.")
        return

    total_average = 0
    highest_average = -1
    lowest_average = 101

    # Calculate class performance
    for name in students:

        average = students[name]["average"]

        total_average = total_average + average

        if average > highest_average:
            highest_average = average

        if average < lowest_average:
            lowest_average = average

    # Calculate student count and class average
    student_count = len(students)
    class_average = total_average / student_count

    # Display class summary
    print("\nClass Summary")
    print("-----------------------------")
    print("Total Students:", student_count)
    print("Class Average:", round(class_average, 2))
    print("Highest Average:", round(highest_average, 2))
    print("Lowest Average:", round(lowest_average, 2))


# FUNCTION 8: MAIN PROGRAM
# Control the complete Student Grade Manager
def main():

    global students

    # Load previous student records when the program starts
    students = load_students()

    while True:

        print("\n===== STUDENT GRADE MANAGER =====")
        print("1. Add Student")
        print("2. Display Student Reports")
        print("3. Display Class Summary")
        print("4. Exit")

        try:
            choice = int(input("Enter your choice: "))

            if choice == 1:
                add_student()

            elif choice == 2:
                display_students()

            elif choice == 3:
                display_class_summary()

            elif choice == 4:
                save_students()
                print("Thank you for using Student Grade Manager.")
                break

            else:
                print("Invalid choice. Please select 1 to 4.")

        except ValueError:
            print("Please enter a number between 1 and 4.")

        except (KeyboardInterrupt, EOFError):
            print("\nProgram stopped.")
            break


# PROGRAM STARTING POINT
# Run the main function when this Python file is executed
if __name__ == "__main__":
    main()
