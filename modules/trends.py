import pandas as pd
import plotly.express as px
import streamlit as st
import requests

from utils.export_report import to_excel

def show_enrollment_trends():
    st.subheader("📈 Enrollment Trends Overview")

    # Fetch data from FastAPI
    try:
        response = requests.get("http://localhost:8000/students")
        response.raise_for_status()
        #st.write("Students Response:", response.text)  # Debug the response
        students_df = pd.DataFrame(response.json())
        
        response = requests.get("http://localhost:8000/enrollment_trends")
        response.raise_for_status()
        #st.write("Enrollment Trends Response:", response.text)  # Debug the response
        trends_df = pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Failed to fetch data: {e}")
        return
    except ValueError as e:
        st.error(f"Failed to parse JSON: {e}")
        return

    # Total Enrollments by Year and Program
    st.markdown("### 🔹 Enrollments Over Years by Program")
    fig1 = px.line(trends_df, x="year", y="total_enrolled", color="program", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # Enrollment Distribution by Gender
    st.markdown("### 🔹 Enrollment Distribution by Gender")
    gender_counts = students_df["gender"].value_counts().reset_index()
    gender_counts.columns = ["gender", "count"]
    fig2 = px.pie(gender_counts, names="gender", values="count", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

    # Enrollment by Semester
    st.markdown("### 🔹 Enrollment Count by Semester")
    semester_counts = students_df["semester"].value_counts().sort_index().reset_index()
    semester_counts.columns = ["semester", "count"]
    fig3 = px.bar(semester_counts, x="semester", y="count", color="semester", text="count")
    st.plotly_chart(fig3, use_container_width=True)

    # Enrollment Status Summary
    st.markdown("### 🔹 Enrollment Status Summary")
    status_counts = students_df["enrollment_status"].value_counts().reset_index()
    status_counts.columns = ["enrollment_status", "count"]
    st.dataframe(status_counts.set_index("enrollment_status"))

    st.markdown("### 📥 Export Enrollment Data")
    excel_data = to_excel(students_df)
    st.download_button(
        label="📄 Download Full Student Enrollment Data as Excel",
        data=excel_data,
        file_name="enrollment_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )