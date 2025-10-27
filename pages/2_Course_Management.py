import streamlit as st
import pandas as pd
import sqlite3
from Utils.db_util_new import init_db, deleteCourse, getCourse, addCourse, updateCourse, getCourses



st.set_page_config(
    layout="wide",
    page_title="Course Management",
    initial_sidebar_state="collapsed"
)


init_db()

if "update_form_ID" not in st.session_state:
    st.session_state.update_form_ID = None
if "add_form_open" not in st.session_state:
    st.session_state.add_form_open = False

st.title("University Course Catalog🎓")

# Fetch Data
rows = getCourses()
df = pd.DataFrame(rows, columns=["Course Code", "Course Name"])

st.subheader("Current Courses")

if st.button("➕ Add a new Course", type="primary"):
    st.session_state.add_form_open = True
    st.session_state.update_form_ID = None

if st.session_state.add_form_open:
    with st.expander("Add a new Course", expanded=True):
        with st.form("add_Course"):
            st.subheader("Enter course details")
            courseCode = st.text_input("Course Code").strip().upper()  # remove extra spaces and convert to upper case
            courseName = st.text_input("Course Name").strip()

            if st.form_submit_button("Add Course"):
                if courseCode != "" and courseName != "":
                    if len(getCourse(courseCode))==0:
                        addCourse(courseCode, courseName)
                        st.session_state.add_form_open = False
                        st.success(f"Course **{courseCode}** added successfully!")   #double star for bold
                        st.rerun()
                    else:
                        st.error(f"Course with code '{courseCode}' already exists.")
                else:
                    st.error("Please provide all details.")

st.markdown("---")  #horizontal line divider


if not rows:
    st.info("Course list is empty.")
else:

    col_ratios = [1, 3, 1, 1] # [Course Code (1), Course Name (3), Update Button (1), Delete Button (1)]

    header_col1, header_col2, header_col3, header_col4 = st.columns(col_ratios)
    with header_col1:
        st.markdown("**Course Code**")
    with header_col2:
        st.markdown("**Course Name**")
    with header_col3:
        st.markdown("**Action**")
    with header_col4:
        st.markdown("**Action**")

    st.markdown("---")

    # 3. Iterate over the rows to display data and create buttons
    for row in rows:
        course_code = row[0]
        course_name = row[1]

        row_col1, row_col2, row_col3, row_col4 = st.columns(col_ratios)

        with row_col1:
            st.text(course_code)
        with row_col2:
            st.text(course_name)

        with row_col3:
            # Update Button
            if st.button("✏️Update", key=f"update_{course_code}", help=f"Update {course_code}"):
                st.session_state.update_form_ID = course_code
                st.session_state.add_form_open = False  # Close add form if open
                st.rerun()

        with row_col4:
            # Delete Button
            if st.button("🗑️Delete", key=f"delete_{course_code}", type="primary", help=f"Delete {course_code}"):
                deleteCourse(course_code)
                st.success(f"Course **{course_code}** deleted.")
                st.rerun()

st.markdown("---")

if st.session_state.update_form_ID:
    with st.expander(f"Update Course: {st.session_state.update_form_ID}", expanded=True):
        course_details = getCourse(st.session_state.update_form_ID)

        if course_details:
            course_detail = course_details[0]

            with st.form("Upd_Course"):
                st.subheader("Course Update Form")

                current_code = course_detail[0]

                newCode = st.text_input("Course Code (New)", value=current_code).strip().upper()
                newName = st.text_input("Course Name", value=course_detail[1]).strip()

                save = st.form_submit_button("Save Changes", type="primary")
                if save:
                    if newCode != "" and newName != "":
                        if newCode != current_code:
                            try:
                                deleteCourse(current_code)
                                addCourse(newCode, newName)
                                st.success(f"Course **{current_code}** successfully changed to **{newCode}**!")
                            except sqlite3.IntegrityError as e:
                                st.error(f"Error changing Course Code: The new code **{newCode}** might already exist or have a constraint issue. ({e})")
                                # Again adding the old course if the change failed to prevent data loss
                                addCourse(current_code, course_detail[1])
                        else:
                            updateCourse(newCode, newName)
                            st.success(f"Course **{newCode}** name updated successfully!")

                        st.session_state.update_form_ID = None
                        st.rerun()
                    else:
                        st.error("Course Code and Name cannot be empty.")
        else:
            st.info("Course not found or may have been deleted.")
            st.session_state.update_form_ID = None