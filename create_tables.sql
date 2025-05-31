-- Drop existing tables if they exist (optional, since you're deleting them manually)
-- DROP TABLE IF EXISTS courses CASCADE;
-- DROP TABLE IF EXISTS enrollment_trends CASCADE;
-- DROP TABLE IF EXISTS faculty CASCADE;
--DROP TABLE IF EXISTS feedback CASCADE;
-- DROP TABLE IF EXISTS graduation CASCADE;
-- DROP TABLE IF EXISTS students CASCADE;

-- Create courses table
-- CREATE TABLE courses (
--     Course_ID VARCHAR(50) PRIMARY KEY,
--     Course_Name VARCHAR(50),
--     Department VARCHAR(50),
--     Semester_Offered INTEGER,
--     Max_Capacity INTEGER,
--     Enrolled_Students_Count INTEGER,
--     Instructor_ID VARCHAR(50)
-- );

-- -- Create enrollment_trends table
-- CREATE TABLE enrollment_trends (
--     Year INTEGER,
--     Program VARCHAR(50),
--     Total_Enrolled INTEGER,
--     Total_Graduated INTEGER,
--     PRIMARY KEY (Year, Program)
-- );

-- -- Create faculty table
-- CREATE TABLE faculty (
--     Instructor_ID VARCHAR(50) PRIMARY KEY,
--     Name VARCHAR(50),
--     Department VARCHAR(50),
--     Average_Student_Feedback_Score FLOAT,
--     Graduation_Success_Rate FLOAT,
--     Course_IDs_Taught VARCHAR(50)
-- );

-- Create feedback table
CREATE TABLE feedback (
    Course_ID VARCHAR(50),
    Instructor_ID VARCHAR(50),
    Student_ID VARCHAR(50),
    Feedback_Score INTEGER,
    Comments VARCHAR(50)
);

-- Create graduation table
-- CREATE TABLE graduation (
--     Student_ID VARCHAR(50) PRIMARY KEY,
--     Name VARCHAR(50),
--     Gender VARCHAR(50),
--     Age INTEGER,
--     Program VARCHAR(50),
--     Semester INTEGER,
--     Enrollment_Year INTEGER,
--     Enrollment_Status VARCHAR(50),
--     Graduation_Year INTEGER,
--     GPA FLOAT,
--     Category VARCHAR(50)
-- );

-- -- Create students table
-- CREATE TABLE students (
--     Student_ID VARCHAR(50) PRIMARY KEY,
--     Name VARCHAR(50),
--     Gender VARCHAR(50),
--     Age INTEGER,
--     Program VARCHAR(50),
--     Semester INTEGER,
--     Enrollment_Year INTEGER,
--     Enrollment_Status VARCHAR(50)
-- );