import pandas
import pandas as pd
import streamlit as st

from Utils.db_util_new import getCourses, getSubjects, getAttendanceDates, getAttendance, init_db, fetchStudents,updateAttendance,deleteAttendancOfSubjectOfDate
import plotly.express as px


st.set_page_config(
    layout="wide",
    page_title="View Attendance",
    initial_sidebar_state="collapsed"
)


if "editAttenceFormON" not in  st.session_state:
    st.session_state.editAttenceFormON=False


init_db()

st.title("View Attendance")

try:
    courses = getCourses()
except Exception as e:
    st.error(f"Error fetching courses: {e}")
    st.stop()

if len(courses) == 0:
    st.error("Please add a course first.")
    st.stop()
else:
    courseCodes = [course[0] for course in courses]
    courseNames = [course[1] for course in courses]


with st.container():
    courseCol, semesterCol, subjectCol = st.columns([1, 1, 1])

    with courseCol:
        selectedCourseName = st.selectbox("Select Course",courseNames)
        selectedCourseCode = courseCodes[courseNames.index(selectedCourseName)]

    with semesterCol:
        selectedSemester = st.number_input(
            "Enter semester",
            min_value=1,
            max_value=8,
        )

    with subjectCol:
        subjects = getSubjects(selectedCourseCode, selectedSemester)
        selectedSubjectCode = None
        if not subjects:
            st.info("No subjects found in current course/semester")
            selectedSubjectCode = None
        else:
            subjectCodes = [subject[0] for subject in subjects]
            subjectNames = [subject[1] for subject in subjects]

            selectedSubject = st.selectbox(
                "Select subject",
                subjectNames,
            )

            selectedSubjectCode=subjectCodes[subjectNames.index(selectedSubject)]

dates=getAttendanceDates(selectedSubjectCode)
if len(dates)==0:
    st.info("No attendance record found for this subject")
else:

    date_col,att_choice_col=st.columns([1,1])

    with date_col:
        new_dates = []
        for date in dates:
            new_dates.append(date[0])

        selectedDate = st.selectbox("Select Date", new_dates)

    with att_choice_col:
        choice=st.selectbox("Show",["All","Present","Absent"])


    
    attendances = getAttendance(selectedSubjectCode, selectedDate)

    enrollIDsPresent = [attendance[1] for attendance in attendances]

    students = fetchStudents(selectedCourseCode)
    enrollIDS = [student[0] for student in students]
    names = [student[1] for student in students]
    status = ["Present" if enroll in enrollIDsPresent else "Absent" for enroll in enrollIDS]

    df = pd.DataFrame({
        "Enrollment No": enrollIDS,
        "Name": names,
        "Status": status
    })

    df.index = df.index + 1

    
    data_col,_,chartCol=st.columns([2,0.5,1.5])

    with data_col:
        
        st.subheader("Attendance list")
        if choice=="All":
            st.dataframe(df)
        else:
            filtered_df = df[df["Status"] == choice]
            st.dataframe(filtered_df)

        edit_btn_col,del_btn_col,=st.columns([1,2])

        with edit_btn_col:
            if st.button("Edit",key="edit_atendance",type="primary"):
                st.session_state.editAttenceFormON=not st.session_state.editAttenceFormON
                st.rerun()

        with del_btn_col:
            if st.button("Delete Attendance Record",type="primary"):
                deleteAttendancOfSubjectOfDate(selectedSubjectCode,selectedDate)
                st.rerun()


        
    

    with chartCol:

        present = len(enrollIDsPresent)
        total = len(students)
        absent = total - present

        # DataFrame
        df = pd.DataFrame({
            "Status": ["Present", "Absent"],
            "Count": [present, absent]
        })

        fig = px.pie(
            df,
            names="Status",
            values="Count",
            color="Status",
            color_discrete_map={"Present": "green", "Absent": "red"},
            hole=0.3
        )

        # Show percentages and values on slices
        fig.update_traces(textinfo='label+percent', hoverinfo='label+value+percent')

        st.subheader("Attendance Overview")
        st.plotly_chart(fig, use_container_width=True)

    if st.session_state.editAttenceFormON:
            with st.expander("Edit Attendace",expanded=True):
                with st.form("Attendace update Form"):
                    st.subheader("Attendance update form")
                    enrollID=st.selectbox("Select Enrollment No",enrollIDS)

                    isPresent=st.checkbox("Present")

                    if st.form_submit_button():
                        if enrollID not in enrollIDS:
                            st.info("Please enter valid enrollment number")
                        else:
                            updateAttendance(enrollID,selectedSubjectCode,selectedDate,isPresent)
                            st.session_state.editAttenceFormON=False
                            st.rerun()

