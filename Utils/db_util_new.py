import sqlite3
import os
from datetime import datetime
from Utils.Paths import DATABASE_FILEPATH


def get_connection():
    os.makedirs("Data",exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILEPATH )
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Courses(
            Course_Code VARCHAR(10) PRIMARY KEY NOT NULL,
            Course_Name VARCHAR(40) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subjects(
            Subject_Code VARCHAR(10) PRIMARY KEY NOT NULL,
            Subject_Name VARCHAR(40) NOT NULL,
            Semester INT,
            Course_ID VARCHAR(40),
            FOREIGN KEY (Course_ID) REFERENCES Courses(Course_Code)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students(
            EnrollID INTEGER PRIMARY KEY NOT NULL,
            Name VARCHAR(30),
            Course VARCHAR(40),
            Image VARCHAR(100),
            FOREIGN KEY (Course) REFERENCES Courses(Course_Code)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attendance (
            Attendance_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EnrollID INTEGER NOT NULL,
            Subject_Code VARCHAR(10),
            Check_In_Time TEXT NOT NULL,
            FOREIGN KEY (EnrollID) REFERENCES Students(EnrollID),
            FOREIGN KEY (Subject_Code) REFERENCES Subjects(Subject_Code)
        )"""
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MetaData(
                   key TEXT PRIMARY KEY,
                   value TEXT
                   )"""
    )

    conn.commit()
    conn.close()
    populateDataIfInitial()

def populateDataIfInitial():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM MetaData WHERE key='initial_data_done'")
    result=cursor.fetchone()

    if result is None:
        cursor.execute("""
            INSERT INTO Courses (Course_Code, Course_Name) VALUES 
                ('BTech_CSE', 'B.Tech Computer Science Engineering'),
                ('BTech_ECE', 'B.Tech Electronics Engineering'),
                ('BSC_N', 'B.Sc Nursing')
        """)

        cursor.execute("""
            INSERT INTO Subjects (Subject_Code, Subject_Name, Semester, Course_ID) VALUES
                ('CSE101', 'Introduction to Programming', 1, 'BTech_CSE'),
                ('CSE102', 'Mathematics I', 1, 'BTech_CSE'),
                ('CSE103', 'Digital Logic Design', 1, 'BTech_CSE'),
                ('CSE104', 'Engineering Physics', 1, 'BTech_CSE'),

                ('ECE101', 'Basic Electrical Engineering', 1, 'BTech_ECE'),
                ('ECE102', 'Applied Physics', 1, 'BTech_ECE'),
                ('ECE103', 'Engineering Mathematics I', 1, 'BTech_ECE'),
                ('ECE104', 'Electronic Devices', 1, 'BTech_ECE')
        """)

        cursor.execute("INSERT INTO MetaData(key,value) VALUES ('initial_data_done','yes')")
        print("Inserted Data")
        conn.commit()

    conn.close()

def executeQuery(query, params=None, isFetch=False):
    if params is None:
        params = []
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if isFetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise e
    finally:
        if conn:
            conn.close()



#for courses
def getCourse(id):
    return executeQuery("SELECT * FROM Courses where Course_Code=?",(id,), isFetch=True)

def getCourses():
    return executeQuery("SELECT * FROM Courses", isFetch=True)

def updateCourse(code,name):
    executeQuery("UPDATE Courses SET Course_Name = ? WHERE Course_Code = ?", (name,code))

def addCourse(code,name):
    executeQuery("INSERT INTO Courses(Course_Code,Course_Name) VALUES (?,?)", (code,name))

def deleteCourse(id):
    executeQuery("DELETE FROM Courses where Course_Code=?",(id,))

#for student

def addStudent(id,name, course,image_path):
    executeQuery("INSERT INTO Students(EnrollID,Name,Course,Image) VALUES (?,?,?,?)",(id,name, course,image_path,))

def fetchStudent(id):
    return executeQuery("SELECT * FROM Students where EnrollID=?",[id,],isFetch=True)

def fetchstudent_of_course(id, course):
    return executeQuery("SELECT * FROM Students where EnrollID=? and Course = ?", [id,course], isFetch=True)



def fetchStudents(course=None):
    if not course:
        return executeQuery("SELECT * FROM Students",[],isFetch=True)
    else:
        return executeQuery("SELECT * FROM Students where Course=?", [course], isFetch=True)

def updateStudent(id, name,course, image_path):
    executeQuery("UPDATE Students SET Name = ?,Course = ?,Image=? WHERE EnrollID = ?",(name, course,image_path, id))

def deleteStudent(id):
    executeQuery("delete from Students where EnrollID=?", [id,])

#for subject
def addSubject(code, name, semester, course_id):
    executeQuery("INSERT INTO Subjects(Subject_Code, Subject_Name, Semester, Course_ID) VALUES (?,?,?,?)",
                 (code, name, semester, course_id))

def getSubjects(course_id=None,semester=None):
    if course_id and semester:
        return executeQuery("SELECT * FROM Subjects WHERE Course_ID = ? and Semester= ?", (course_id,semester), isFetch=True)
    else:
        return executeQuery("SELECT * FROM Subjects", isFetch=True)

def getSubject(subjectCode):
    return executeQuery("SELECT * FROM Subjects WHERE Subject_Code = ?", (subjectCode,), isFetch=True)

def updateSubject(code, name, semester, course_id):
    executeQuery("UPDATE Subjects SET Subject_Name = ?, Semester = ?, Course_ID = ? WHERE Subject_Code = ?",
                 (name, semester, course_id, code))

def deleteSubject(code):
    executeQuery("DELETE FROM Subjects WHERE Subject_Code = ?", (code,))


#for attendance

#Attendance_ID (auto),EnrollID ,Subject_Code Check_In_Time

def markAttendance(enrollNo,subjectCode,ctime):
    executeQuery("INSERT INTO Attendance(EnrollID ,Subject_Code,Check_In_Time) VALUES (?,?,?)",(enrollNo,subjectCode,ctime))

def getAttendance(subject_code=None,date=None):
    return executeQuery("SELECT * FROM Attendance where Subject_Code=? and DATE(Check_In_Time)=? ORDER BY EnrollID", [subject_code,date], isFetch=True)

def getAttendanceDates(subject_code):
    return executeQuery("SELECT DISTINCT DATE(Check_In_Time) AS Attendance_Date FROM Attendance where Subject_Code=? ORDER BY Attendance_Date DESC;",[subject_code], isFetch=True)

def isMarked(enroll, subjectCode, cTime):

    result = executeQuery(
        "Select * from Attendance where EnrollID = ? and Subject_Code = ? and DATE(Check_In_Time)=DATE(?)", (enroll, subjectCode, cTime),isFetch=True)

    return len(result) >0

def deleteAttendancOfSubjectOfDate(subjectCode,date):
    executeQuery("DELETE FROM Attendance where  Subject_Code= ? and DATE(Check_In_Time)=DATE(?)",(subjectCode,date))

def deleteStudentAttendance(enrollID,subjectCode,date):
    executeQuery("DELETE FROM Attendance where  Subject_Code= ? and EnrollID =? and DATE(Check_In_Time)=DATE(?)",(subjectCode,enrollID,date))


def updateAttendance(enroll, subject, date, isPresent):
 
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d 00:00:00")
    else:
        date_str = str(date).split(" ")[0] + " 00:00:00"

    if isPresent:
        if not isMarked(enroll, subject, date_str):
            markAttendance(enroll, subject, date_str)
            print(f"Attendance marked for {enroll} on {date_str}")
        else:
            print(f"Already marked for {enroll} on {date_str}")
    else:
        if isMarked(enroll, subject, date_str):
            deleteStudentAttendance(enroll, subject, date_str)
            print(f"Attendance removed for {enroll} on {date_str}")
        else:
            print(f"No record found to delete for {enroll} on {date_str}")





