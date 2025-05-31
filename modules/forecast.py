import pandas as pd
import streamlit as st
from prophet import Prophet
import plotly.graph_objects as go
import plotly.express as px
import requests
from utils.export_report import to_excel

def fetch_data(endpoint):
    """Helper function to fetch data from FastAPI endpoint."""
    try:
        response = requests.get(f"http://localhost:8000/{endpoint}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Failed to fetch {endpoint} data: {e}")
        return pd.DataFrame()
    except ValueError as e:
        st.error(f"Failed to parse {endpoint} JSON: {e}")
        return pd.DataFrame()

def show_enrollment_forecast():
    st.subheader("🔮 Future Enrollment Forecasting")

    # Fetch data from FastAPI
    trends_df = fetch_data("enrollment_trends")
    students_df = fetch_data("students")
    courses_df = fetch_data("courses")
    graduation_df = fetch_data("graduation")
    feedback_df = fetch_data("feedback")

    # Check if primary dataset is empty
    if trends_df.empty:
        st.warning("Enrollment trends data is empty.")
        return

    # --- Program Enrollment Forecast ---
    st.markdown("### 📈 Program Enrollment Forecast")
    programs = trends_df["program"].unique()
    selected_program = st.selectbox("Select a Program to Forecast", programs)

    df_filtered = trends_df[trends_df["program"] == selected_program]
    df_prophet = df_filtered[["year", "total_enrolled"]].rename(columns={"year": "ds", "total_enrolled": "y"})
    df_prophet["ds"] = pd.to_datetime(df_prophet["ds"], format="%Y")

    # Train forecasting model
    model = Prophet(yearly_seasonality=True)
    model.fit(df_prophet)

    # Future data frame
    future = model.make_future_dataframe(periods=3, freq="Y")
    forecast = model.predict(future)

    # Plot forecast
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_prophet["ds"], y=df_prophet["y"], mode='markers+lines', name='Actual'))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], mode='lines', name='Forecast'))
    fig.update_layout(title=f"Enrollment Forecast for {selected_program}", xaxis_title="Year", yaxis_title="Enrollment")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Forecasted Enrollments for next 3 years in {selected_program}:**")
    st.dataframe(forecast[["ds", "yhat"]].tail(3).rename(columns={"ds": "Year", "yhat": "Predicted_Enrollment"}))

    # --- Course Enrollment Forecast ---
    if not courses_df.empty:
        st.markdown("### 📚 Course Enrollment Forecast")
        departments = courses_df["department"].unique()
        selected_dept = st.selectbox("Select a Department for Course Forecast", departments)

        dept_courses = courses_df[courses_df["department"] == selected_dept]
        course_enrollment = dept_courses.groupby("course_name")["enrolled_students_count"].sum().reset_index()
        course_enrollment = course_enrollment.merge(courses_df[["course_name", "department"]], on="course_name")

        # Check for valid enrollment data
        if course_enrollment["enrolled_students_count"].isnull().any() or course_enrollment["enrolled_students_count"].eq(0).all():
            st.warning(f"No valid enrollment data available for {selected_dept}. Cannot generate forecast.")
        else:
            # Mock historical data (since courses_df lacks year column)
            # Ideally, fetch historical data from a proper endpoint
            years = [2021, 2022, 2023, 2024]  # Mock years
            historical_data = []
            for year in years:
                temp_df = course_enrollment.copy()
                temp_df["year"] = year
                # Simulate historical data by scaling enrollments (for demo purposes)
                temp_df["enrolled_students_count"] = temp_df["enrolled_students_count"] * (0.8 + 0.05 * (year - 2021))
                historical_data.append(temp_df)
            
            course_enrollment_historical = pd.concat(historical_data, ignore_index=True)
            df_course_prophet = course_enrollment_historical[["year", "enrolled_students_count"]].rename(columns={"year": "ds", "enrolled_students_count": "y"})
            df_course_prophet["ds"] = pd.to_datetime(df_course_prophet["ds"], format="%Y")
            
            # Ensure sufficient data points
            if len(df_course_prophet["ds"].unique()) < 2:
                st.warning(f"Insufficient historical data for {selected_dept}. At least two years of data are required for forecasting.")
            else:
                # Clean data: Remove NaN or invalid values
                df_course_prophet = df_course_prophet.dropna()
                if df_course_prophet.empty:
                    st.warning(f"No valid data points after cleaning for {selected_dept}. Cannot generate forecast.")
                else:
                    # Train course forecasting model
                    try:
                        model_course = Prophet(yearly_seasonality=True)
                        model_course.fit(df_course_prophet)

                        # Future data frame for courses
                        future_course = model_course.make_future_dataframe(periods=3, freq="Y")
                        forecast_course = model_course.predict(future_course)

                        # Plot course forecast
                        fig_course = go.Figure()
                        fig_course.add_trace(go.Scatter(x=df_course_prophet["ds"], y=df_course_prophet["y"], mode='markers+lines', name='Actual'))
                        fig_course.add_trace(go.Scatter(x=forecast_course["ds"], y=forecast_course["yhat"], mode='lines', name='Forecast'))
                        fig_course.update_layout(title=f"Course Enrollment Forecast for {selected_dept}", xaxis_title="Year", yaxis_title="Enrollment")
                        st.plotly_chart(fig_course, use_container_width=True)

                        st.markdown(f"**Forecasted Course Enrollments for next 3 years in {selected_dept}:**")
                        st.dataframe(forecast_course[["ds", "yhat"]].tail(3).rename(columns={"ds": "Year", "yhat": "Predicted_Enrollment"}))
                    except Exception as e:
                        st.error(f"Failed to generate course forecast: {e}")

    # --- Graduation Rate Forecast ---
    if not graduation_df.empty:
        st.markdown("### 🎓 Graduation Rate Forecast")
        grad_by_year = graduation_df["graduation_year"].value_counts().sort_index().reset_index()
        grad_by_year.columns = ["year", "count"]
        df_grad_prophet = grad_by_year.rename(columns={"year": "ds", "count": "y"})
        df_grad_prophet["ds"] = pd.to_datetime(df_grad_prophet["ds"], format="%Y")

        # Train graduation forecasting model
        model_grad = Prophet(yearly_seasonality=True)
        model_grad.fit(df_grad_prophet)

        # Future data frame for graduation
        future_grad = model_grad.make_future_dataframe(periods=3, freq="Y")
        forecast_grad = model_grad.predict(future_grad)

        # Plot graduation forecast
        fig_grad = go.Figure()
        fig_grad.add_trace(go.Scatter(x=df_grad_prophet["ds"], y=df_grad_prophet["y"], mode='markers+lines', name='Actual'))
        fig_grad.add_trace(go.Scatter(x=forecast_grad["ds"], y=forecast_grad["yhat"], mode='lines', name='Forecast'))
        fig_grad.update_layout(title="Graduation Rate Forecast", xaxis_title="Year", yaxis_title="Number of Graduates")
        st.plotly_chart(fig_grad, use_container_width=True)

        st.markdown("**Forecasted Graduation Rates for next 3 years:**")
        st.dataframe(forecast_grad[["ds", "yhat"]].tail(3).rename(columns={"ds": "Year", "yhat": "Predicted_Graduates"}))

    # --- Export Forecast Data ---
    st.markdown("### 📥 Export Forecast Data")
    combined_forecast = forecast[["ds", "yhat"]].rename(columns={"ds": "Year", "yhat": f"Predicted_Enrollment_{selected_program}"})
    if not courses_df.empty and not course_enrollment["enrolled_students_count"].isnull().any() and len(df_course_prophet["ds"].unique()) >= 2:
        combined_forecast = combined_forecast.merge(
            forecast_course[["ds", "yhat"]].rename(columns={"ds": "Year", "yhat": f"Predicted_Course_Enrollment_{selected_dept}"}),
            on="Year", how="outer"
        )
    if not graduation_df.empty:
        combined_forecast = combined_forecast.merge(
            forecast_grad[["ds", "yhat"]].rename(columns={"ds": "Year", "yhat": "Predicted_Graduates"}),
            on="Year", how="outer"
        )
    
    excel_data = to_excel(combined_forecast)
    st.download_button(
        label="📄 Download Forecast Data as Excel",
        data=excel_data,
        file_name="forecast_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    st.title("Forecasting Dashboard")
    show_enrollment_forecast()