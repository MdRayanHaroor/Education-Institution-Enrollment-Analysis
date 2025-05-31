import pandas as pd

def load_students_data():
    return pd.read_csv("data/students.csv")

def load_courses_data():
    return pd.read_csv("data/courses.csv")

def load_graduation_data():
    return pd.read_csv("data/graduation.csv")

def load_faculty_data():
    return pd.read_csv("data/faculty.csv")

def load_enrollment_trends_data():
    return pd.read_csv("data/enrollment_trends.csv")

def load_feedback_data():
    return pd.read_csv("data/feedback.csv")
