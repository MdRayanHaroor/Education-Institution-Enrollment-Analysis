import pandas as pd
import plotly.express as px
import streamlit as st
import requests

from utils.export_report import to_excel

def show_feedback_analysis():
    st.subheader("🗣️ Feedback & Evaluation Analysis")

    # Fetch data from FastAPI
    try:
        response = requests.get("http://localhost:8000/feedback")
        response.raise_for_status()
        #st.write("Feedback Response:", response.text)  # Debug the response
        feedback_df = pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Failed to fetch feedback data: {e}")
        return
    except ValueError as e:
        st.error(f"Failed to parse JSON: {e}")
        return

    if feedback_df.empty:
        st.warning("Feedback data is empty.")
        return

    # Score Distribution Histogram
    st.markdown("### 📊 Feedback Score Distribution")
    fig1 = px.histogram(
        feedback_df,
        x="feedback_score",
        nbins=10,
        title="Distribution of Feedback Scores",
        color_discrete_sequence=["#3f72af"]
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Average Feedback Score per Instructor
    st.markdown("### 👨‍🏫 Average Feedback Score per Instructor")
    avg_scores = feedback_df.groupby("instructor_id")["feedback_score"].mean().reset_index()
    avg_scores.columns = ["instructor_id", "average_score"]
    fig2 = px.bar(
        avg_scores,
        x="instructor_id",
        y="average_score",
        color="average_score",
        text="average_score"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Show Raw Feedback Table
    with st.expander("🔍 View Raw Feedback Data"):
        st.dataframe(feedback_df)

    st.markdown("### 📥 Export Feedback Data")
    excel_data = to_excel(feedback_df)
    st.download_button(
        label="📄 Download Feedback Data as Excel",
        data=excel_data,
        file_name="feedback_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )