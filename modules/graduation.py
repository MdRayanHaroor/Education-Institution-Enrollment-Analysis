import pandas as pd
import plotly.express as px
import streamlit as st
import os
import requests

from utils.export_report import to_excel
from utils.export_pdf import generate_pdf

def show_graduation_analysis():
    st.subheader("🎓 Graduation Rate & Demographics Analysis")

    # Fetch data from FastAPI
    try:
        response = requests.get("http://localhost:8000/graduation")
        response.raise_for_status()
        graduation_df = pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Failed to fetch graduation data: {e}")
        return
    except ValueError as e:
        st.error(f"Failed to parse JSON: {e}")
        return

    if graduation_df.empty:
        st.warning("Graduation data is empty.")
        return

    # Graduation count by year
    st.markdown("### 📅 Graduation Count by Year")
    grad_by_year = graduation_df["graduation_year"].value_counts().sort_index().reset_index()
    grad_by_year.columns = ["year", "count"]
    fig1 = px.bar(grad_by_year, x="year", y="count", text="count", color="count")
    st.plotly_chart(fig1, use_container_width=True)

    # Graduation by Gender
    if "gender" in graduation_df.columns:
        st.markdown("### ⚥ Graduation by Gender")
        gender_counts = graduation_df["gender"].value_counts().reset_index()
        gender_counts.columns = ["gender", "count"]
        fig2 = px.pie(gender_counts, names="gender", values="count", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    # Graduation by Category
    if "category" in graduation_df.columns:
        st.markdown("### 🏷 Graduation by Category")
        cat_counts = graduation_df["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        fig3 = px.bar(cat_counts, x="category", y="count", text="count", color="category")
        st.plotly_chart(fig3, use_container_width=True)

    # GPA Distribution
    st.markdown("### 🎓 GPA Distribution of Graduates")
    fig4 = px.histogram(graduation_df, x="gpa", nbins=20, title="GPA Histogram", color_discrete_sequence=["#4CAF50"])
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### 📥 Export Graduation Data")
    excel_data = to_excel(graduation_df)
    st.download_button(
        label="📄 Download Graduation Data as Excel",
        data=excel_data,
        file_name="graduation_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("### 🖨 Export Graduation Data as PDF")
    if st.button("📄 Generate PDF Report"):
        # Convert DataFrame to list of lists
        data = [graduation_df.columns.tolist()] + graduation_df.head(30).values.tolist()
        
        # Define column renames (original_name: display_name)
        column_renames = {
            "enrollment_year": "Enrollment<br/>Year",
            "graduation_year": "Graduation<br/>Year",
            "student_id": "Student<br/>ID",
            "program": "Program"
        }
        
        pdf_file = generate_pdf(
            title="Graduation Report",
            data=data,
            logo_path="assets/logo.png",
            column_renames=column_renames,
            columns_to_remove=["enrollment_status"]
        )
        
        st.download_button(
            label="📥 Download PDF",
            data=pdf_file,
            file_name="graduation_report.pdf",
            mime="application/pdf"
        )