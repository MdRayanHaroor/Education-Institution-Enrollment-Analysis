from http.client import HTTPException
import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from prophet import Prophet

load_dotenv()
app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres%403@localhost:5432/Project")
engine = create_engine(DATABASE_URL)

# Test database connection
try:
    with engine.connect() as connection:
        print("Database connected successfully!")
except Exception as e:
    print(f"Failed to connect to the database: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models
class Student(Base):
    __tablename__ = "students"
    student_id = Column(String, primary_key=True)
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    program = Column(String)
    semester = Column(Integer)
    enrollment_year = Column(Integer)
    enrollment_status = Column(String)

class EnrollmentTrend(Base):
    __tablename__ = "enrollment_trends"
    year = Column(Integer, primary_key=True)
    program = Column(String, primary_key=True)
    total_enrolled = Column(Integer)
    total_graduated = Column(Integer)

class Feedback(Base):
    __tablename__ = "feedback"
    # No primary key specified; assuming composite key or auto-incremented ID
    course_id = Column(String, primary_key=True)
    instructor_id = Column(String, primary_key=True)
    student_id = Column(String, primary_key=True)
    feedback_score = Column(Integer)
    comments = Column(String)

class Faculty(Base):
    __tablename__ = "faculty"
    instructor_id = Column(String, primary_key=True)
    name = Column(String)
    department = Column(String)
    average_student_feedback_score = Column(Float)
    graduation_success_rate = Column(Float)
    course_ids_taught = Column(String)

class Course(Base):
    __tablename__ = "courses"
    course_id = Column(String, primary_key=True)
    course_name = Column(String)
    department = Column(String)
    semester_offered = Column(Integer)
    max_capacity = Column(Integer)
    enrolled_students_count = Column(Integer)
    instructor_id = Column(String)

class Graduation(Base):
    __tablename__ = "graduation"
    student_id = Column(String, primary_key=True)
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    program = Column(String)
    semester = Column(Integer)
    enrollment_year = Column(Integer)
    enrollment_status = Column(String)
    graduation_year = Column(Integer)
    gpa = Column(Float)
    category = Column(String)

# Pydantic Models
class StudentModel(BaseModel):
    student_id: str
    name: str
    gender: str
    age: int
    program: str
    semester: int
    enrollment_year: int
    enrollment_status: str

class EnrollmentTrendModel(BaseModel):
    year: int
    program: str
    total_enrolled: int
    total_graduated: int

class FeedbackModel(BaseModel):
    course_id: str
    instructor_id: str
    student_id: str
    feedback_score: int
    comments: Optional[str] = None

class FacultyModel(BaseModel):
    instructor_id: str
    name: str
    department: str
    average_student_feedback_score: float
    graduation_success_rate: float
    course_ids_taught: str

class CourseModel(BaseModel):
    course_id: str
    course_name: str
    department: str
    semester_offered: int
    max_capacity: int
    enrolled_students_count: int
    instructor_id: str

class GraduationModel(BaseModel):
    student_id: str
    name: str
    gender: str
    age: int
    program: str
    semester: int
    enrollment_year: int
    enrollment_status: str
    graduation_year: int
    gpa: float
    category: str

class ForecastModel(BaseModel):
    year: str  # ISO format date (e.g., "2025-12-31")
    predicted_enrollment: Optional[float] = None
    predicted_course_enrollment: Optional[float] = None
    predicted_graduates: Optional[float] = None
    program: Optional[str] = None
    department: Optional[str] = None

# Endpoints
@app.get("/students", response_model=List[StudentModel])
def get_students():
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        return students
    finally:
        db.close()

@app.get("/enrollment_trends", response_model=List[EnrollmentTrendModel])
def get_enrollment_trends():
    db = SessionLocal()
    try:
        trends = db.query(EnrollmentTrend).all()
        return trends
    finally:
        db.close()

@app.get("/feedback", response_model=List[FeedbackModel])
def get_feedback():
    db = SessionLocal()
    try:
        feedback = db.query(Feedback).all()
        return feedback
    finally:
        db.close()

@app.get("/faculty", response_model=List[FacultyModel])
def get_faculty():
    db = SessionLocal()
    try:
        faculty = db.query(Faculty).all()
        return faculty
    finally:
        db.close()

@app.get("/courses", response_model=List[CourseModel])
def get_courses():
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        return courses
    finally:
        db.close()

@app.get("/graduation", response_model=List[GraduationModel])
def get_graduation():
    db = SessionLocal()
    try:
        graduation = db.query(Graduation).all()
        return graduation
    finally:
        db.close()

# Forecast Endpoint
@app.get("/forecast", response_model=List[ForecastModel])
def get_forecast(program: Optional[str] = None, department: Optional[str] = None):
    db = SessionLocal()
    try:
        # Fetch data
        trends_df = pd.read_sql(db.query(EnrollmentTrend).statement, db.bind)
        courses_df = pd.read_sql(db.query(Course).statement, db.bind)
        graduation_df = pd.read_sql(db.query(Graduation).statement, db.bind)

        forecasts = []

        # Program Enrollment Forecast
        if not trends_df.empty and program:
            df_filtered = trends_df[trends_df["program"] == program]
            if not df_filtered.empty:
                df_prophet = df_filtered[["year", "total_enrolled"]].rename(columns={"year": "ds", "total_enrolled": "y"})
                df_prophet["ds"] = pd.to_datetime(df_prophet["ds"], format="%Y")
                df_prophet = df_prophet.dropna()
                
                if len(df_prophet["ds"].unique()) >= 2 and not df_prophet["y"].le(0).all():
                    model = Prophet(yearly_seasonality=True, growth="linear")
                    model.add_floor(0)  # Enforce non-negative predictions
                    model.fit(df_prophet)
                    future = model.make_future_dataframe(periods=3, freq="Y")
                    forecast = model.predict(future)
                    
                    for _, row in forecast[["ds", "yhat"]].tail(3).iterrows():
                        forecasts.append({
                            "year": row["ds"].strftime("%Y-%m-%d"),
                            "predicted_enrollment": max(0, round(row["yhat"], 2)),
                            "program": program
                        })
                else:
                    raise HTTPException(400, detail=f"Insufficient or invalid data for program {program} forecast")

        # Course Enrollment Forecast
        if not courses_df.empty and department:
            dept_courses = courses_df[courses_df["department"] == department]
            if not dept_courses.empty:
                course_enrollment = dept_courses.groupby("course_name")["enrolled_students_count"].sum().reset_index()
                
                # Mock historical data
                years = [2021, 2022, 2023, 2024]
                historical_data = []
                for year in years:
                    temp_df = course_enrollment.copy()
                    temp_df["year"] = year
                    temp_df["enrolled_students_count"] = temp_df["enrolled_students_count"] * (0.8 + 0.05 * (year - 2021))
                    historical_data.append(temp_df)
                
                course_enrollment_historical = pd.concat(historical_data, ignore_index=True)
                df_course_prophet = course_enrollment_historical[["year", "enrolled_students_count"]].rename(
                    columns={"year": "ds", "enrolled_students_count": "y"}
                )
                df_course_prophet["ds"] = pd.to_datetime(df_course_prophet["ds"], format="%Y")
                df_course_prophet = df_prophet.dropna()
                
                if len(df_course_prophet["ds"].unique()) >= 2 and not df_course_prophet["y"].le(0).all():
                    model_course = Prophet(yearly_seasonality=True, growth="linear")
                    model_course.add_floor(0)  # Enforce non-negative predictions
                    model_course.fit(df_course_prophet)
                    future_course = model_course.make_future_dataframe(periods=3, freq="Y")
                    forecast_course = model_course.predict(future_course)
                    
                    for _, row in forecast_course[["ds", "yhat"]].tail(3).iterrows():
                        forecasts.append({
                            "year": row["ds"].strftime("%Y-%m-%d"),
                            "predicted_course_enrollment": max(0, round(row["yhat"], 2)),
                            "department": department
                        })
                else:
                    raise HTTPException(400, detail=f"Insufficient or invalid data for department {department} forecast")

        # Graduation Rate Forecast
        if not graduation_df.empty:
            grad_by_year = graduation_df["graduation_year"].value_counts().sort_index().reset_index()
            grad_by_year.columns = ["year", "count"]
            df_grad_prophet = grad_by_year.rename(columns={"year": "ds", "count": "y"})
            df_grad_prophet["ds"] = pd.to_datetime(df_grad_prophet["ds"], format="%Y")
            df_grad_prophet = df_grad_prophet.dropna()
            
            if len(df_grad_prophet["ds"].unique()) >= 2 and not df_grad_prophet["y"].le(0).all():
                model_grad = Prophet(yearly_seasonality=True, growth="linear")
                model_grad.add_floor(0)  # Enforce non-negative predictions
                model_grad.fit(df_grad_prophet)
                future_grad = model_grad.make_future_dataframe(periods=3, freq="Y")
                forecast_grad = model_grad.predict(future_grad)
                
                for _, row in forecast_grad[["ds", "yhat"]].tail(3).iterrows():
                    forecasts.append({
                        "year": row["ds"].strftime("%Y-%m-%d"),
                        "predicted_graduates": max(0, round(row["yhat"], 2))
                    })
            else:
                raise HTTPException(400, detail="Insufficient or invalid data for graduation rate forecast")

        if not forecasts:
            raise HTTPException(400, detail="No forecasts generated due to insufficient or invalid data")

        return forecasts

    except Exception as e:
        raise HTTPException()
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)