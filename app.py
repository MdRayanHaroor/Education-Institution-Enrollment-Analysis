import pandas as pd
import requests
import streamlit as st
# from utils.load_data import (
#     load_students_data,
#     load_courses_data,
#     load_graduation_data,
#     load_faculty_data,
#     load_enrollment_trends_data,
#     load_feedback_data
# )
from modules.trends import show_enrollment_trends
from modules.graduation import show_graduation_analysis
from modules.courses import show_course_analysis
from modules.faculty import show_faculty_analysis
from modules.feedback import show_feedback_analysis
from modules.forecast import show_enrollment_forecast

st.set_page_config(page_title="Educational Institution Enrolment Dashboard", layout="wide")

st.title("📊 Educational Institution Enrolment Dashboard")
st.markdown("Welcome! Use the sidebar to explore different insights.")

# Sidebar
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["👥 Students", "📚 Courses", "🎓 Graduation", "👨‍🏫 Faculty", "📈 Trends", "🗣 Feedback", "🔮 Forecast"])

# Load datasets
# students_df = load_students_data()
# courses_df = load_courses_data()
# graduation_df = load_graduation_data()
# faculty_df = load_faculty_data()
# trends_df = load_enrollment_trends_data()
# feedback_df = load_feedback_data()

# Simple table previews for each section
if section == "👥 Students":
    st.subheader("Students Data")
    # Since we're fetching data in other sections, you might want to fetch /students here too
    try:
        #response = requests.get("http://localhost:8000/students")
        response = requests.get("http://127.0.0.1:8000/students")
        response.raise_for_status()
        students_df = pd.DataFrame(response.json())
        st.dataframe(students_df)
    except requests.RequestException as e:
        st.error(f"Failed to fetch students data: {e}")
        
elif section == "📚 Courses":
    st.subheader("Courses Data")
    show_course_analysis()

elif section == "🎓 Graduation":
    st.subheader("Graduation Data")
    show_graduation_analysis()
    #st.dataframe(graduation_df)

elif section == "👨‍🏫 Faculty":
    st.subheader("Faculty Data")
    show_faculty_analysis()

elif section == "📈 Trends":
    st.subheader("Enrollment Trends Data")
    show_enrollment_trends()
    #st.dataframe(trends_df)

elif section == "🗣 Feedback":
    st.subheader("Feedback Data")
    show_feedback_analysis()

elif section == "🔮 Forecast":
    st.subheader("Enrollment Forecast")
    show_enrollment_forecast()
