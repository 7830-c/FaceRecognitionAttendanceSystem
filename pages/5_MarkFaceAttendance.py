import pickle
import cv2
import streamlit as st
import face_recognition
import numpy as np
import cvzone
import time
import datetime
import plotly.express as px

from Utils.Paths import encodingFileName
from Utils.db_util_new import init_db, getCourses, getSubjects, markAttendance, isMarked, getAttendance, \
    fetchstudent_of_course, fetchStudents

camera=0

st.set_page_config(
    page_title="Take Attendance",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#state setting
if "attendance_running" not in st.session_state:
    st.session_state.attendance_running = False
if "attendanceImgData" not in st.session_state:
    st.session_state.attendanceImgData = []
if "attendanceNameData" not in st.session_state:
    st.session_state.attendanceNameData = []
if "attendanceSIDData" not in st.session_state:
    st.session_state.attendanceSIDData = []
if "selected_subject_name" not in st.session_state:
    st.session_state.selected_subject_name = None
if "selected_subject_code" not in st.session_state:
    st.session_state.selected_subject_code = None
if "selected_course_code" not in st.session_state:
    st.session_state.selected_course_code = None
if "selected_semester" not in st.session_state:
    st.session_state.selected_semester = 1
if "attendanceDisplayedSID" not in st.session_state:
    st.session_state.attendanceDisplayedSID = []

init_db()

st.title("🎥 Real-Time Face Attendance using OpenCV")


try:
    with open(encodingFileName, "rb") as file:
        encodedData = pickle.load(file)
    ids, names, knownEncodedEmbeddings = encodedData
except FileNotFoundError:
    st.warning(f"⚠️ Encoding file '{encodingFileName}' not found. Please add students first.")
    st.stop()

try:
    courses = getCourses()
except Exception as e:
    st.error(f"Error fetching courses: {e}")
    st.stop()

if len(courses) == 0:
    st.error("Please add a course first.")
    st.stop()

def start_attendance(subject_name, subject_code, course_code, semester):
    st.session_state.attendance_running = True
    st.session_state.selected_subject_name = subject_name
    st.session_state.selected_subject_code = subject_code
    st.session_state.selected_course_code = course_code
    st.session_state.selected_semester = semester

    #empty previous session data
    st.session_state.attendanceImgData = []
    st.session_state.attendanceNameData = []
    st.session_state.attendanceSIDData = []

    st.rerun()


def reset_session():
    st.session_state.attendance_running = False
    st.session_state.attendanceImgData = []
    st.session_state.attendanceNameData = []
    st.session_state.attendanceSIDData = []
    st.session_state.selected_subject_name = None
    st.session_state.selected_subject_code = None
    st.rerun()


#data selection(course,semster,subject)
if not st.session_state.attendance_running and st.session_state.selected_subject_name is None:

    courseCodes = [course[0] for course in courses]
    courseNames = [course[1] for course in courses]

    with st.container():
        st.subheader("Select Course and Subject")
        courseCol, semesterCol, subjectCol = st.columns([1, 1, 1])

        index=0
        if st.session_state.selected_course_code in courseCodes:
            index=courseCodes.index(st.session_state.selected_course_code)

        with courseCol:
            selectedCourseName = st.selectbox(
                "Select Course",
                courseNames,
                index=index
            )
            selectedCourseCode = courseCodes[courseNames.index(selectedCourseName)]

        with semesterCol:
            selectedSemester = st.number_input(
                "Enter semester",
                value=st.session_state.selected_semester,
                min_value=1,
                max_value=8,
            )

        # Update session state for next rerun
        st.session_state.selected_course_code = selectedCourseCode
        st.session_state.selected_semester = selectedSemester

        with subjectCol:
            subjects = getSubjects(selectedCourseCode, selectedSemester)
            selectedSubject = None

            if not subjects:
                st.info("No subjects found in current course/semester")
                selectedSubjectCode = None
            else:
                subjectCodes = [subject[0] for subject in subjects]
                subjectNames = [subject[1] for subject in subjects]

                default_index = 0
                if st.session_state.selected_subject_name in subjectNames:
                    default_index = subjectNames.index(st.session_state.selected_subject_name)

                selectedSubject = st.selectbox(
                    "Select subject",
                    subjectNames,
                    index=default_index,
                )

                if selectedSubject:
                    selectedSubjectCode = subjectCodes[subjectNames.index(selectedSubject)]
                else:
                    selectedSubjectCode = subjectCodes[default_index]  # Fallback to first subject code

    if selectedSubjectCode is not None and st.button("🎬 Start Attendance", key="start_btn", type="primary"):
        res=getAttendance(selectedSubjectCode, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if len(res)==0:
            start_attendance(selectedSubject, selectedSubjectCode, selectedCourseCode, selectedSemester)
        else:
            st.info("Attendance for this subject has already taken for today")

elif st.session_state.attendance_running:

    main_layout, _, list_layout = st.columns([3, 0.5, 1.5])

    with main_layout:
        st.subheader(f"Live Attendance for: {st.session_state.selected_subject_name}")
        frame_holder = st.empty()
        status_text = st.empty()

        if st.button("🟥 Stop Attendance", type="primary", help="Stop Attendance", key="stop_btn"):
            st.session_state.attendance_running = False
            st.rerun()

    with list_layout:
        st.subheader("Live Attendance List")
        attendance_expander = st.expander("Attendance List", expanded=True)
        list_placeholder = attendance_expander.container()

    status_text.info("🟢 Attendance Running... Detecting faces.")

    cap = cv2.VideoCapture(camera)

    while st.session_state.attendance_running:
        success, img = cap.read()
        if not success:
            status_text.error("❌ Failed to access webcam!")
            st.session_state.attendance_running = False
            break

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25) #resizing for faster processing
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesLocations = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesLocations)

        attendance_marked_in_frame = False

        for encodeFace, faceLoc in zip(encodesCurFrame, facesLocations):
            matches = face_recognition.compare_faces(knownEncodedEmbeddings, encodeFace)
            faceDistances = face_recognition.face_distance(knownEncodedEmbeddings, encodeFace)
            best_match_index = np.argmin(faceDistances)

            name = "Unknown"
            student_id = None
            res=0
            student=None
            marked=False

            if matches[best_match_index] and faceDistances[best_match_index] < 0.5: #0.5 distance tolerance
                name = names[best_match_index].upper()
                student_id = ids[best_match_index]
                student=fetchstudent_of_course(student_id,st.session_state.selected_course_code)
                res=len(student)

                marked=isMarked(student_id,st.session_state.selected_subject_code,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if res==0:
                color = (0, 0, 255)  # Red for Unknown
                name="Unknown"
            elif marked and res!=0:
                color = (255, 0, 0)  # blue
                name="Marked Already"
            else:
                color = (0, 255, 0)  # Green for Known

                if not marked:
                    if student_id not in st.session_state.attendanceSIDData and res: #only mark when not marked earlier
                        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        markAttendance(student_id, st.session_state.selected_subject_code, currentTime)

                        # Add details to show in attendanceList
                        try:
                            student_id, student_name,course,img_path = student[0]

                            # Append data to session state
                            st.session_state.attendanceSIDData.append(student_id)
                            st.session_state.attendanceImgData.append(img_path)
                            st.session_state.attendanceNameData.append(student_name)
                            attendance_marked_in_frame = True

                        except Exception as e:
                            print(f"Error fetching student data for list: {e}")

            top, right, bottom, left = faceLoc
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
            bbox = (left, top, right - left, bottom - top)

            img = cvzone.cornerRect(img, bbox, rt=0, colorC=color)
            img, _ = cvzone.putTextRect(img, name, (left, top - 20), scale=2, thickness=2, colorR=color,offset=10)

        if attendance_marked_in_frame:
            with list_placeholder:
                for student_id, img_p, name in zip(
                        reversed(st.session_state.attendanceSIDData),
                        reversed(st.session_state.attendanceImgData),
                        reversed(st.session_state.attendanceNameData)
                ):
                    if student_id not in st.session_state.attendanceDisplayedSID:
                        img_col, name_col = st.columns([1, 1])
                        with img_col:
                            st.image(img_p, width=40)
                        with name_col:
                            st.markdown(f"**{name}** ✅")
                        st.markdown("---")

                        st.session_state.attendanceDisplayedSID.append(student_id)

        frame_holder.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), channels="RGB")
        time.sleep(0.01)


    cap.release()
    cv2.destroyAllWindows()


elif not st.session_state.attendance_running and st.session_state.selected_subject_name is not None: #summary

    main_layout, _, list_layout = st.columns([3, 0.5, 1.5])

    with main_layout:
        st.subheader("Attendance Session Summary")

        noStudentsPresent = len(st.session_state.attendanceSIDData)
        st.metric(label=f"Total Students Marked for {st.session_state.selected_subject_name}", value= noStudentsPresent)
        total_students=len(fetchStudents(st.session_state.selected_course_code))
        absent=total_students-noStudentsPresent

        colors = {"Present": "green", "Absent": "red"}
        fig = px.pie(
            names=["Present", "Absent"],
            values=[noStudentsPresent, absent],
            color=["Present", "Absent"],
            color_discrete_map=colors,  # ✅ use color_discrete_map for dict mapping
            hole=0.3
        )

        st.subheader("Attendance Overview")
        st.plotly_chart(fig,use_container_width=True)


        if st.button("➕ Start New Attendance", type="secondary", key="new_session_btn"):
            reset_session()

    with list_layout:
        st.subheader("Final Attendance List")

        if st.session_state.attendanceNameData:
            with st.expander("Attendance List", expanded=True):
                head_col1, head_col2 = st.columns([1, 1])
                with head_col1:
                    st.write("**Image**")
                with head_col2:
                    st.write("**Name**")

                for img_p, name in zip(
                        reversed(st.session_state.attendanceImgData),
                        reversed(st.session_state.attendanceNameData)
                ):
                    img_col, name_col = st.columns([1, 1])
                    with img_col:
                        st.image(img_p, width=40)
                    with name_col:
                        st.markdown(f"**{name}** ✅")
                    st.markdown("---")
        else:
            st.info("No students were marked during this session.")
