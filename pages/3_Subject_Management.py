import streamlit as st

from Utils.db_util_new import getCourses, getSubjects, addSubject, getSubject, deleteSubject,updateSubject


st.set_page_config(
    layout="wide",
    page_title="Subject Management",
    initial_sidebar_state="collapsed"
)

if "updateSubjectId" not in st.session_state:
    st.session_state.updateSubjectId = None

if "addSubjectForm_on" not in st.session_state:
    st.session_state.addSubjectForm_on=False

add_button_text="Add Subject"

st.title("Subject Management")
courses=getCourses()

if len(courses)==0:
    st.info("Please add a course first.")
else:
    courseCodes=[course[0] for course in courses]
    courseNames = [course[1] for course in courses]

    courseCol,semsterCol=st.columns([1,1])
    with courseCol:
        courseName=st.selectbox("Select the course",courseNames)
    with semsterCol:
        semester=st.number_input("Enter Semster",value=1,min_value=1,max_value=8)

    courseCode=courseCodes[courseNames.index(courseName)]

    if st.session_state.addSubjectForm_on and st.session_state.updateSubjectId is None:
        with st.expander("Add a new Subject", expanded=True):
            with st.form("add_Subject"):
                st.subheader("Enter subject details")
                subjectCode = st.text_input("Subject Code").strip().upper()
                subjectName = st.text_input("Subject Name").strip()

                if st.form_submit_button("Add",type="primary"):
                    if subjectCode != "" and subjectName != "":
                        if len(getSubject(subjectCode)) == 0:
                            addSubject(subjectCode,subjectName,semester,courseCodes[courseNames.index(courseName)])
                            st.session_state.addSubjectForm_on = False
                            st.success(f"Subject**{subjectCode}** added successfully!")
                            st.session_state.addSubjectForm_on=False
                            st.rerun()
                        else:
                            st.error(f"Subject with code '{subjectCode}' already exists.")
                    else:
                        st.error("Please provide all details.")


    subjects=getSubjects(courseCode,semester)
    if st.button("Add Subject",type="primary"):
        st.session_state.updateSubjectId=None
        st.session_state.addSubjectForm_on=not st.session_state.addSubjectForm_on
        st.rerun()


    if len(subjects)==0:
        st.info(f"Subject list for course {courseName} and Semester {semester} is empty")
    else:
        st.header(f"Subjects in course {courseName}")

        content_col,blank_col=st.columns([2,1])

        with content_col:
            col_ratios=[1,2,1,1]

            st.markdown("---")
            header_col1,header_col2,header_col3,header_col4=st.columns(col_ratios)

            with header_col1:
                st.markdown("**Subject Code**")
            with header_col2:
                st.markdown("**Subject Name**")
            with header_col3:
                st.markdown("**Action**")
            with header_col4:
                st.markdown("**Action**")

            st.markdown("---")

            for subject in subjects:
                code_col,name_col,update_col,del_col=st.columns(col_ratios)

                with code_col:
                    st.text(subject[0])
                with name_col:
                    st.text(subject[1])
                with update_col:
                    if st.button("Update",help=f"Update {subject[0]}",type="primary",key=f"update_{subject[0]}"):
                        st.session_state.updateSubjectId=subject[0]
                        st.session_state.addSubjectForm_on=False
                with del_col:
                    if st.button("Delete", help=f"Delete {subject[0]}", type="primary",key=f"delete_{subject[0]}"):
                        deleteSubject(subject[0])
                        st.rerun()



if st.session_state.updateSubjectId and not st.session_state.addSubjectForm_on:
    subject=getSubject(st.session_state.updateSubjectId)[0]
    cSubjectCode=subject[0]
    cSubjectName=subject[1]
    cSemester=subject[2]
    cCourseCode=subject[3]

    with st.expander(f"Update subject", expanded=True):
        with st.form("update_Subject"):
            st.subheader("Enter updated details")
            subjectCode = st.text_input("Subject Code",value=cSubjectCode).strip().upper()
            subjectName = st.text_input("Subject Name",value=cSubjectName).strip()
            semester=st.number_input("Semester",min_value=1,max_value=8,value=cSemester)

            selectedIndex=courseCodes.index(cCourseCode)
            selectedCourseName = st.selectbox("Select the course", courseNames,index=selectedIndex)

            if st.form_submit_button("Save Changes",type="primary"):
                if subjectCode != "" and subjectName != "":
                    if subjectCode!=subject[0]:#change subject code
                        if len(getSubject(subjectCode))!=0:
                            st.error("Subject with same subject code already exist.")
                        else:
                            deleteSubject(subject[0])
                            addSubject(subjectCode,subjectName,semester,courseCodes[courseNames.index(selectedCourseName)])
                            st.session_state.updateSubjectId=None
                            st.rerun()
                    else:
                        updateSubject(subject[0],subjectName,semester,courseCodes[courseNames.index(selectedCourseName)])
                        st.session_state.updateSubjectId = None
                        st.rerun()
                else:
                    st.error("Please provide all details.")
