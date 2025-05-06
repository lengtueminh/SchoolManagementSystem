import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="tueminh25",    # CHANGE PASSWORD HERE 
            database="SchoolManagementSystem"
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None
    
def get_teacher_name(teacher_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT TeacherName FROM Teachers WHERE TeacherCode = %s"
            cursor.execute(query, (teacher_code,))
            result = cursor.fetchone()
            if result:
                return result[0]  
            else:
                return None
        except Error as e:
            print(f"Error fetching teacher name: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_teacher_details(teacher_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT TeacherName, Email, TeacherCode, Subject FROM Teachers WHERE TeacherCode = %s"
            cursor.execute(query, (teacher_code,))
            result = cursor.fetchone()
            if result:
                return {
                    "teacher_name": result[0],
                    "email": result[1],
                    "teacher_code": result[2],
                    "subject": result[3]
                }
            else:
                return None
        except Error as e:
            print(f"Error fetching teacher details: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_teacher_classes(teacher_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT C.ClassName, T.Subject
                FROM Classes AS C LEFT JOIN Teachers AS T
                    ON C.TeacherID = T.TeacherID
                WHERE T.TeacherCode = %s
            """
            cursor.execute(query, (teacher_code,))
            result = cursor.fetchall()
            classes = [{"class_name": row[0], "subject_name": row[1]} for row in result]
            return classes
        except Error as e:
            print(f"Error fetching teacher classes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def get_student_name(student_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT StudentName FROM Students WHERE StudentCode = %s"
            cursor.execute(query, (student_code,))
            result = cursor.fetchone()
            if result:
                return result[0]  
            else:
                return None
        except Error as e:
            print(f"Error fetching teacher name: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_student_details(student_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT StudentName, StudentID, StudentCode, BirthDate, ClassID, Address FROM Students WHERE StudentCode = %s"
            cursor.execute(query, (student_code,))
            result = cursor.fetchone()
            if result:
                return {
                    "student_name": result[0], 
                    "student_id": result[1], 
                    "student_code": result[2], 
                    "birthdate": result[3], 
                    "class_id": result[4], 
                    "address": result[5]	
                }
            else:
                return None
        except Error as e:
            print(f"Error fetching student details: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_student_classes(student_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """ 
            CALL GetSubjectsAndTeachersFromCode(%s);
            """
            cursor.execute(query, (student_code,))
            result = cursor.fetchall()
            classes = [
                {
                    "subject_name": row[0],
                    "teacher_name": row[1]
                }
                for row in result
            ]
            return classes
        except Error as e:
            print(f"Error fetching student classes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []



def update_student_details(student_code, new_name, new_address):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                UPDATE Students
                SET StudentName = %s, Address = %s
                WHERE StudentCode = %s
            """
            cursor.execute(query, (new_name, new_address, student_code))
            connection.commit()
            return True
        except Exception as e:
            print(f"Failed to update student: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False


def get_student_grades(student_code):
    conn = connect_db()  # Kết nối cơ sở dữ liệu
    cursor = conn.cursor(dictionary=True)

    # Gọi Stored Procedure GetStudentSubjectsGradesByCode để lấy điểm theo môn
    cursor.callproc('GetStudentSubjectsGradesByCode', [student_code])
    
    # Gọi Stored Procedure GetStudentGPAByCode để lấy GPA tổng
    cursor.callproc('GetStudentGPAByCode', [student_code])

    result_subjects = []
    result_gpa_total = None

    # Lấy dữ liệu bảng điểm từng môn
    for result in cursor.stored_results():
        if result.column_names == ('SubjectName', 'Score_10', 'Score_40', 'Score_50', 'GPA_Subject'):
            result_subjects = result.fetchall()
        elif result.column_names == ('GPA_Total',):
            result_gpa_total = result.fetchone()

    conn.close()
    
    # Trả về bảng điểm môn học và GPA tổng
    return result_subjects, result_gpa_total['GPA_Total'] if result_gpa_total else None

def update_teacher_details(teacher_code, new_name, new_email):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                UPDATE Teachers
                SET TeacherName = %s, Email = %s
                WHERE TeacherCode = %s
            """
            cursor.execute(query, (new_name, new_email, teacher_code))
            connection.commit()
            return True
        except Exception as e:
            print(f"Failed to update teacher details: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def submit_grade_to_db(student_code, teacher_code, grade, percentage):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()

            # Lấy TeacherID từ TeacherCode
            cursor.execute("SELECT TeacherID FROM Teachers WHERE TeacherCode = %s", (teacher_code,))
            teacher_result = cursor.fetchone()
            if not teacher_result:
                return False
            teacher_id = teacher_result[0]

            # lấy studentid từ student code
            cursor.execute("SELECT StudentID FROM Students WHERE StudentCode = %s", (student_code,))
            student_result = cursor.fetchone()
            if not student_result:
                return False
            student_id = student_result[0]

            # Lấy SubjectID mà giáo viên đang dạy
            cursor.execute("SELECT SubjectID FROM Classes WHERE TeacherID = %s LIMIT 1", (teacher_id,))
            subject_result = cursor.fetchone()
            if not subject_result:
                return False
            subject_id = subject_result[0]

            # Cập nhật hoặc chèn điểm
            cursor.execute("SELECT * FROM Grades WHERE StudentID = %s AND SubjectID = %s", (student_id, subject_id))
            if cursor.fetchone():
                cursor.execute("UPDATE Grades SET Grade = %s WHERE StudentID = %s AND SubjectID = %s", (grade, student_id, subject_id))
            else:
                cursor.execute("INSERT INTO Grades (StudentID, SubjectID, Grade) VALUES (%s, %s, %s)", (student_id, subject_id, grade))

            connection.commit()
            return True

        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def check_student_exists(student_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM Students WHERE StudentCode = %s", (student_code,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Error checking student existence: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

