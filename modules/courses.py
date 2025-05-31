import pandas as pd
import plotly.express as px
import streamlit as st
import requests

from utils.export_report import to_excel

def show_course_analysis():
    st.subheader("📚 Course Popularity & Capacity Planning")

    # Fetch course data from FastAPI
    try:
        response = requests.get("http://localhost:8000/courses")
        response.raise_for_status()
        courses_df = pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Failed to fetch course data: {e}")
        return
    except ValueError as e:
        st.error(f"Failed to parse course JSON: {e}")
        return

    if courses_df.empty:
        st.warning("Courses data is empty.")
        return

    # Top 10 popular courses by enrollment
    st.markdown("### 🔝 Top 10 Most Enrolled Courses")
    top_courses = courses_df.sort_values(by="enrolled_students_count", ascending=False).head(10)
    fig1 = px.bar(top_courses, x="enrolled_students_count", y="course_name", orientation="h",
                  color="enrolled_students_count", text="enrolled_students_count")
    st.plotly_chart(fig1, use_container_width=True)

    # Enrollment vs Capacity
    st.markdown("### 📊 Course Enrollment vs Capacity")
    fig2 = px.bar(
        courses_df,
        x="course_name",
        y=["enrolled_students_count", "max_capacity"],
        barmode="group",
        title="Enrollment vs Capacity"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Department-wise Course Count
    st.markdown("### 🏛 Department-wise Course Count")
    dept_counts = courses_df["department"].value_counts().reset_index()
    dept_counts.columns = ["department", "course_count"]
    fig3 = px.pie(dept_counts, names="department", values="course_count", hole=0.4)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 📥 Export Course Data")
    excel_data = to_excel(courses_df)
    st.download_button(
        label="📄 Download Courses Data as Excel",
        data=excel_data,
        file_name="courses_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    st.title("Course Trends Dashboard")
    show_course_trends()