import os
import streamlit as st

from Utils.Paths import Student_IMG_DIR
from Utils.ImageUtils import saveImage, generateEncodings, removeEncoding
from Utils.db_util_new import init_db, deleteStudent, fetchStudents, updateStudent, addStudent, getCourses,fetchStudent



os.makedirs(Student_IMG_DIR,exist_ok=True)

st.set_page_config(
    layout="wide",
    page_title="Student Management",
    initial_sidebar_state="collapsed"
)

#session state management
if "imageToShow" not in st.session_state:
    st.session_state.imageToShow = None
    st.session_state.imageHeading = "Selected Image"

if "updateId" not in st.session_state:
    st.session_state.updateId = None

if "addStudentForm_on" not in st.session_state:
    st.session_state.addStudentForm_on=False


#page first time loading
if "first_load" not in st.session_state:
    st.session_state.first_load = True
    st.session_state.updateId = None
else:
    st.session_state.first_load = False

init_db()
st.title("Registered Students")
rows = fetchStudents()


if st.button("Add new Student",type="primary"):
    st.session_state.addStudentForm_on=True
    st.session_state.updateId = None


if st.session_state.addStudentForm_on:
    courses = getCourses()
    if len(courses) == 0:
        st.info("No courses present to enroll student")
        st.session_state.addStudentForm_on = False
    else:
        with st.expander("Student Data Form",expanded=True):
                with st.form("addStudentForm"):
                    st.subheader("Enter Student Details")
                    enrollNo = st.text_input("Enter Enrollment No.")
                    name = st.text_input("Enter Student Name")
                    courseCode=[]
                    courseName=[]
                    for course in courses:
                        courseCode.append(course[0])
                        courseName.append(course[1])

                    selectedCourse=st.selectbox("Course to enroll student in",options=courseName)
                    img = st.file_uploader("Upload picture", type=[".png", ".jpeg", ".jpg"])
                    if st.form_submit_button():
                        if enrollNo and name and selectedCourse and img is not None:
                            if len(fetchStudent(enrollNo))==0:
                                img_path = saveImage(img, enrollNo, name)
                                encodingResult=generateEncodings(img_path,enrollNo,name)

                                if encodingResult==1:
                                    addStudent(enrollNo,name,courseCode[courseName.index(selectedCourse)],img_path)
                                    st.success("Student added")
                                else:
                                    st.info("Zero or multiple faces detected in uploaded image.Choose other picture")

                            else:
                                st.info("Student with same enrollment no already present")

                        st.session_state.addStudentForm_on = False
                        st.rerun()


COL_RATIOS_Data_Side = [2,2.5,2,1.5, 1.5,1.5]

if rows:
    # Dividing page for data table and image viewer
    data_side, img_side = st.columns([3, 1])

    with data_side:
        header_col1, header_col2, header_col3, header_col4, header_col5,header_col6 = st.columns(COL_RATIOS_Data_Side)
        with header_col1:
            st.markdown("**Enroll No**")
        with header_col2:
            st.markdown("**Name**")
        with header_col3:
            st.markdown("**Course**")
        with header_col4:
            st.markdown("**View Image**")
        with header_col5:
            st.markdown("**Action**")
        with header_col6:
            st.markdown("**Action**")

        st.markdown("---")

        for row in rows:
            enrollNo,name,course,image_path = row

            enrollNo_col, name_col,course_col, img_btn_col, update_btn_col, del_btn_col = st.columns(COL_RATIOS_Data_Side)

            with enrollNo_col:
                st.markdown(f"**{enrollNo}**")
            with name_col:
                st.write(name)
            with course_col:
                st.markdown(f"**{course}**")

            with img_btn_col:
                if st.button("View Image", key=f"img_{enrollNo}",help="View Student Image"):
                    st.session_state.imageToShow = image_path
                    st.session_state.imageHeading = f"**{name}**"

            # Update Button
            with update_btn_col:
                if st.button("✏️Update", key=f"update_{enrollNo}", type="primary"):
                    st.session_state.updateId = enrollNo
                    st.rerun()

            # Delete Button
            with del_btn_col:
                if st.button("🗑️Delete", key=f"delete_{enrollNo}", type="primary"):
                    student_to_delete = [r for r in rows if r[0] == enrollNo][0]
                    deleteStudent(enrollNo)

                    old_path = os.path.join(Student_IMG_DIR, f"{student_to_delete[0]}_{student_to_delete[1]}.png")
                    if os.path.exists(old_path):
                        os.remove(old_path)

                    removeEncoding(enrollNo)

                    st.success(f"Person **{name} (ID: {enrollNo})** deleted.")
                    st.rerun()

    with img_side:
        st.subheader(st.session_state.imageHeading)
        if st.session_state.imageToShow and os.path.exists(st.session_state.imageToShow):
            st.image(st.session_state.imageToShow, width=150)
            if st.button("Hide Image", key="hide_img_btn"):
                st.session_state.imageToShow = None
                st.session_state.imageHeading = "Selected Image"
                st.rerun()
        else:
            st.info("Click 'View' to see the image.")
            if st.session_state.imageToShow and not os.path.exists(st.session_state.imageToShow):
                st.session_state.imageToShow = None
                st.warning("Image file not found on disk.")
else:
    st.info("Currently no student is added.")

if st.session_state.updateId:
    id_to_update = st.session_state.updateId

    student_to_update = [r for r in rows if r[0] == id_to_update][0]

    with st.expander(f"**Student details Update Form**", expanded=True):

        # load previous data
        courses = getCourses()
        courseCodes = [course[0] for course in courses]
        courseNames = [course[1] for course in courses]

        current_course_code = student_to_update[2]
        current_course_name = courses[courseCodes.index(current_course_code)][1]

        with st.form("UpdateForm", clear_on_submit=False):
            st.subheader(f"Edit details of student: **{student_to_update[1]}**")
            new_name = st.text_input("Name", value=student_to_update[1]).strip()
            new_course = st.selectbox("Select Course", courseNames, index=courseNames.index(current_course_name))
            new_img = st.file_uploader("Upload New Image", type=[".jpg", ".png", ".jpeg"])

            submitted = st.form_submit_button("Save Changes", type="primary")

            if submitted:
                id_to_update = student_to_update[0]
                current_name = student_to_update[1]
                old_path = os.path.join(Student_IMG_DIR, f"{id_to_update}_{current_name}.png")

                final_path = old_path

                if new_img is not None:
                    if os.path.exists(old_path):
                        os.remove(old_path)

                    final_path = saveImage(new_img, id_to_update, new_name)
                    print(f"New image saved to: {final_path}")

                elif new_name != current_name:
                    new_file_name = f"{id_to_update}_{new_name}.png"
                    final_path = os.path.join(Student_IMG_DIR, new_file_name)
                    if os.path.exists(old_path):
                        os.rename(old_path, final_path)
                        print(f"Image renamed from {old_path} to {final_path}")

                if new_name and new_course:
                    res = generateEncodings(final_path, id_to_update, new_name)
                    if res == 1:
                        updateStudent(id_to_update, new_name, courseCodes[courseNames.index(new_course)], final_path)
                        st.session_state.updateId = None
                        st.session_state.imageToShow = None
                        st.success("Details and encoding updated successfully! Check console for mock updates.")
                        st.rerun()
                    elif res == 0:
                        st.info("No face detected in image. Select another image.")
                    else:
                        st.info("Multiple faces detected in image. Select another image.")
                else:
                    st.info("Please ensure Name and Course are filled.")
