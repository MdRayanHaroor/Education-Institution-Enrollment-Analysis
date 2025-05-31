import pandas as pd
import plotly.express as px
import streamlit as st
import requests

from utils.export_report import to_excel

def show_faculty_analysis():
    st.subheader("👩‍🏫 Faculty Performance Analysis")

    # Fetch data from FastAPI
    try:
        response = requests.get("http://localhost:8000/faculty")
        response.raise_for_status()
        #st.write("Faculty Response:", response.text)  # Debug the response
        faculty_df = pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Failed to fetch faculty data: {e}")
        return
    except ValueError as e:
        st.error(f"Failed to parse JSON: {e}")
        return

    if faculty_df.empty:
        st.warning("Faculty data is empty.")
        return

    # Average Student Feedback Score by Instructor
    st.markdown("### 📊 Average Student Feedback Score by Instructor")
    fig1 = px.bar(
        faculty_df,
        x="average_student_feedback_score",
        y="name",
        color="department",
        text="average_student_feedback_score",
        orientation="h",
        title="Average Feedback Score per Instructor"
    )
    fig1.update_traces(texttemplate="%{text:.2f}", textposition="auto")
    st.plotly_chart(fig1, use_container_width=True)

    # Graduation Success Rate by Instructor
    st.markdown("### 🎓 Graduation Success Rate by Instructor")
    fig2 = px.bar(
        faculty_df,
        x="graduation_success_rate",
        y="name",
        color="department",
        text="graduation_success_rate",
        orientation="h",
        title="Graduation Success Rate per Instructor"
    )
    fig2.update_traces(texttemplate="%{text:.2f}%", textposition="auto")
    st.plotly_chart(fig2, use_container_width=True)

    # Department-wise Feedback Score Distribution
    st.markdown("### 🏬 Feedback Score Distribution by Department")
    fig3 = px.box(
        faculty_df,
        x="department",
        y="average_student_feedback_score",
        title="Feedback Score Distribution by Department",
        color="department"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Faculty Summary Table
    st.markdown("### 📋 Faculty Summary")
    summary_df = faculty_df[["name", "department", "average_student_feedback_score", "graduation_success_rate"]]
    st.dataframe(summary_df.set_index("name"))

    # Export Faculty Data
    st.markdown("### 📥 Export Faculty Data")
    excel_data = to_excel(faculty_df)
    st.download_button(
        label="📄 Download Faculty Data as Excel",
        data=excel_data,
        file_name="faculty_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )