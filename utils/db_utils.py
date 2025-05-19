import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'your_password'),
            database=os.getenv('DB_NAME', 'SchoolManagementSystem')
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def fetch_all(query, params=None):
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"Error executing query '{query}': {err}")
            return None
        finally:
            cursor.close()
            conn.close()
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
            query = """
            SELECT T.TeacherName, T.Email, T.TeacherCode, S.SubjectName 
            FROM Teachers  AS T LEFT JOIN Subjects AS S 
                ON T.SubjectID = S.SubjectID
            WHERE TeacherCode = %s"""
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
                SELECT C.ClassName
                FROM Teacher_Class AS TC 
                    LEFT JOIN Teachers AS T ON TC.TeacherID = T.TeacherID
                    LEFT JOIN Classes AS C ON TC.ClassID = C.ClassID
                WHERE T.TeacherCode = %s
            """
            cursor.execute(query, (teacher_code,))
            result = cursor.fetchall()
            classes = [{"class_name": row[0]} for row in result]
            return classes
        except Error as e:
            print(f"Error fetching teacher classes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

## giữ cnay hoặc cái trên
def get_classes_by_teacher(teacher_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT c.ClassID, c.ClassName
                FROM Classes c
                JOIN Teacher_Class tc ON c.ClassID = tc.ClassID
                JOIN Teachers t ON tc.TeacherID = t.TeacherID
                WHERE t.TeacherCode = %s
            """
            cursor.execute(query, (teacher_code,))
            return cursor.fetchall()  # [(ClassID, ClassName), ...]
        except Error as e:
            print(f"Error fetching classes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def get_students_in_class(class_id):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT s.StudentID, s.StudentCode, s.StudentName
                FROM Students s
                WHERE s.ClassID = %s
            """
            cursor.execute(query, (class_id,))
            return cursor.fetchall()  # [(StudentID, StudentCode, StudentName), ...]
        except Error as e:
            print(f"Error fetching students: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def get_students_in_class_with_gpa(class_id, subject_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT 
            st.StudentID,
            st.StudentCode,
            st.StudentName,
            ROUND(
                COALESCE(MAX(CASE WHEN g.Percentage = 0.10 THEN g.Score END) * 0.10, 0) +
                COALESCE(MAX(CASE WHEN g.Percentage = 0.40 THEN g.Score END) * 0.40, 0) +
                COALESCE(MAX(CASE WHEN g.Percentage = 0.50 THEN g.Score END) * 0.50, 0),
                2
            ) AS GPA
        FROM 
            Students st
        LEFT JOIN Grades g ON st.StudentID = g.StudentID AND g.SubjectID = %s
        WHERE 
            st.ClassID = %s
        GROUP BY 
            st.StudentID, st.StudentCode, st.StudentName
    """
    cursor.execute(query, (subject_id, class_id))
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result  # List of (StudentID, StudentCode, StudentName, GPA)

def get_student_grade(student_code, subject_id):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT g.Score
                FROM Grades g
                JOIN Subjects s ON g.SubjectID = s.SubjectID
                WHERE g.StudentID = (SELECT StudentID FROM Students WHERE StudentCode = %s) 
                AND g.SubjectID = %s
            """
            cursor.execute(query, (student_code, subject_id))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Error as e:
            print(f"Error fetching grade: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

#########################

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

def update_student_grade(teacher_code, student_code, subject_id, percentage, grade):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Call the stored procedure
        cursor.callproc('UpdateGrade', (teacher_code, student_code, subject_id, percentage, grade))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("Error updating grade:", e)
        if conn:
            conn.rollback()
            conn.close()
        return False

def get_student_id_by_code(student_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT StudentID FROM Students WHERE StudentCode = %s", (student_code,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


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

    for result in cursor.stored_results():
        if result.column_names == ('SubjectName', 'Score_10', 'Score_40', 'Score_50', 'GPA_Subject'):
            result_subjects = result.fetchall()
        elif result.column_names == ('GPA_Total',):
            result_gpa_total = result.fetchone()

    conn.close()
    
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

def submit_grade_to_db(teacher_code, student_code, subject_id, percentage, grade):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Call the stored procedure to add the grade
        cursor.callproc('AddGradeWithTeacherCode', (teacher_code, student_code, subject_id, percentage, grade))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error submitting grade: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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

def get_all_students():
    query = """
        SELECT 
            s.StudentID AS id,
            s.StudentCode AS code,
            s.StudentName AS name,
            s.BirthDate AS birthdate,
            c.ClassName AS classname,
            s.Address AS address
        FROM Students s
        JOIN Classes c ON s.ClassID = c.ClassID
    """
    return fetch_all(query)

def get_all_teachers():
    query = """
        SELECT 
            t.TeacherID AS id,
            t.TeacherCode AS code,
            t.TeacherName AS name,
            s.SubjectName AS subjectname,
            t.Email AS email
        FROM Teachers t
        JOIN Subjects s ON t.SubjectID = s.SubjectID
        ORDER BY t.TeacherID ASC
    """
    return fetch_all(query)

def get_all_classes():
    query = """
        SELECT 
            c.ClassID AS id,
            c.ClassName AS classname,
            COUNT(s.StudentID) AS total_students
        FROM Classes c
        LEFT JOIN Students s ON c.ClassID = s.ClassID
        GROUP BY c.ClassID, c.ClassName
        ORDER BY c.ClassID ASC
    """
    return fetch_all(query)

def get_all_subjects():
    query = """
        SELECT 
            s.SubjectID AS subjectid,
            s.SubjectName AS subjectname,
            COUNT(t.TeacherID) AS total_teachers
        FROM Subjects s
        LEFT JOIN Teachers t ON s.SubjectID = t.SubjectID
        GROUP BY s.SubjectID, s.SubjectName
        ORDER BY s.SubjectID ASC
    """
    return fetch_all(query)

def get_student_grade_details(student_code, subject_id): 
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT 
        s.SubjectName,
        MAX(CASE WHEN g.Percentage = 0.10 THEN g.Score ELSE NULL END) AS Attendance,
        MAX(CASE WHEN g.Percentage = 0.40 THEN g.Score ELSE NULL END) AS Midterm,
        MAX(CASE WHEN g.Percentage = 0.50 THEN g.Score ELSE NULL END) AS Final,
        ROUND(
            COALESCE(MAX(CASE WHEN g.Percentage = 0.10 THEN g.Score END) * 0.10, 0) +
            COALESCE(MAX(CASE WHEN g.Percentage = 0.40 THEN g.Score END) * 0.40, 0) +
            COALESCE(MAX(CASE WHEN g.Percentage = 0.50 THEN g.Score END) * 0.50, 0),
            2
        ) AS GPA
    FROM Grades g
    JOIN Subjects s ON g.SubjectID = s.SubjectID
    JOIN Students st ON g.StudentID = st.StudentID
    WHERE st.StudentCode = %s AND g.SubjectID = %s
    GROUP BY s.SubjectName
    """

    cursor.execute(query, (student_code, subject_id))
    result = cursor.fetchone()
    conn.close()
    return result  # subject_name, attendance, midterm, final, gpa

def get_subject_id_by_teacher_code(teacher_code):
    
    conn = connect_db()
    cursor = conn.cursor()
    query = """
    SELECT SubjectID FROM Teachers WHERE TeacherCode = %s
    """
    cursor.execute(query, (teacher_code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None

def get_class_name_by_id(class_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT ClassName FROM Classes WHERE ClassID = %s"
    cursor.execute(query, (class_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Unknown Class"

def get_students_of_class(class_id):
    """Get all students in a specific class"""
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT s.StudentID AS id, s.StudentCode AS code, s.StudentName AS name, s.BirthDate AS birthdate, c.ClassName AS classname, s.Address AS address
        FROM Students s
        JOIN Classes c ON s.ClassID = c.ClassID
        WHERE s.ClassID = %s
        ORDER BY s.StudentName
        """
        
        cursor.execute(query, (class_id,))
        students = cursor.fetchall()
        
        # Convert datetime objects to strings
        for student in students:
            if student['birthdate']:
                student['birthdate'] = student['birthdate'].strftime('%Y-%m-%d')
        
        return students
        
    except Exception as e:
        print(f"Error getting students of class: {str(e)}")
        return []
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def ad_update_student_details(student_code, new_name, new_address, new_birthdate, new_class_id):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                UPDATE Students
                SET StudentName = %s, Address = %s, BirthDate = %s, ClassID = %s
                WHERE StudentCode = %s
            """
            cursor.execute(query, (new_name, new_address, new_birthdate, new_class_id, student_code))
            connection.commit()
            return True
        except Exception as e:
            print(f"Failed to update student: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def ad_update_teacher_details(teacher_code, new_name, new_subject_id, new_email):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = 'UPDATE Teachers SET TeacherName = %s, SubjectID = %s, Email = %s WHERE TeacherCode = %s'
            print(f"Updating teacher with teacher_code={teacher_code}, new_name={new_name}, new_subject_id={new_subject_id}, new_email={new_email}")
            cursor.execute(query, (new_name, new_subject_id, new_email, teacher_code))
            connection.commit()
            return True
        except Exception as e:
            print(f"Failed to update teacher: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def ad_add_student(name, address, birthdate, class_id):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = 'INSERT INTO Students (StudentName, Address, BirthDate, ClassID) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (name, address, birthdate, class_id))
            connection.commit()
            return True
        except Exception as e:
            print(f"Failed to add student: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

# Thêm giáo viên mới (không tạo mã, mã do DB tự động tạo)
def ad_add_teacher(name, subject_id, email):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = 'INSERT INTO Teachers (TeacherName, SubjectID, Email) VALUES (%s, %s, %s)'
            print(f"Adding teacher with name={name}, subject_id={subject_id}, email={email}")
            cursor.execute(query, (name, subject_id, email))
            connection.commit()
            return True
        except Exception as e:
            print(f"Failed to add teacher: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

# Thêm lớp học mới
def ad_add_class(classname):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Classes (ClassName)
            VALUES (%s)
        ''', (classname,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to add class: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Thêm môn học mới
def ad_add_subject(subjectname):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Subjects (SubjectName)
            VALUES (%s)
        ''', (subjectname,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to add subject: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Xóa học sinh theo mã
def ad_delete_student(student_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()

            # Step 1: Get the StudentID for the given StudentCode
            cursor.execute('SELECT StudentID FROM Students WHERE StudentCode = %s', (student_code,))
            result = cursor.fetchone()
            if not result:
                print(f"Student with StudentCode {student_code} not found.")
                return False

            student_id = result[0]

            # Step 2: Delete dependent records from Grades table
            cursor.execute('DELETE FROM Grades WHERE StudentID = %s', (student_id,))
            connection.commit()

            # Step 3: Delete dependent records from Users table
            cursor.execute('DELETE FROM Users WHERE StudentID = %s', (student_id,))
            connection.commit()

            # Step 4: Delete the student from Students table
            cursor.execute('DELETE FROM Students WHERE StudentCode = %s', (student_code,))
            connection.commit()

            return cursor.rowcount > 0
        except Exception as e:
            print(f"Failed to delete student: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

# Xóa giáo viên theo mã
def ad_delete_teacher(teacher_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()

            # Step 1: Get the TeacherID for the given TeacherCode
            cursor.execute('SELECT TeacherID FROM Teachers WHERE TeacherCode = %s', (teacher_code,))
            result = cursor.fetchone()
            if not result:
                print(f"Teacher with TeacherCode {teacher_code} not found.")
                return False

            teacher_id = result[0]

            # Step 2: Delete dependent records from Teacher_Class table
            cursor.execute('DELETE FROM Teacher_Class WHERE TeacherID = %s', (teacher_id,))
            connection.commit()

            # Step 3: Delete dependent records from Users table
            cursor.execute('DELETE FROM Users WHERE TeacherID = %s', (teacher_id,))
            connection.commit()

            # Step 4: Delete the teacher from Teachers table
            cursor.execute('DELETE FROM Teachers WHERE TeacherCode = %s', (teacher_code,))
            connection.commit()

            return cursor.rowcount > 0
        except Exception as e:
            print(f"Failed to delete teacher: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

# Xóa lớp học theo ID
def ad_delete_class(class_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        # 1. Xóa các bản ghi teacher_class liên quan đến lớp này
        cursor.execute('DELETE FROM Teacher_Class WHERE ClassID = %s', (class_id,))
        conn.commit()
        # 2. Lấy danh sách StudentID thuộc lớp này
        cursor.execute('SELECT StudentID FROM Students WHERE ClassID = %s', (class_id,))
        student_ids = [row[0] for row in cursor.fetchall()]
        # 3. Xóa điểm và user liên quan đến các học sinh này
        if student_ids:
            format_strings = ','.join(['%s'] * len(student_ids))
            cursor.execute(f'DELETE FROM Grades WHERE StudentID IN ({format_strings})', tuple(student_ids))
            conn.commit()
            cursor.execute(f'DELETE FROM Users WHERE StudentID IN ({format_strings})', tuple(student_ids))
            conn.commit()
        # 4. Xóa tất cả học sinh thuộc lớp này
        cursor.execute('DELETE FROM Students WHERE ClassID = %s', (class_id,))
        conn.commit()
        # 5. Xóa lớp
        cursor.execute('DELETE FROM Classes WHERE ClassID = %s', (class_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Failed to delete class: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Xóa môn học theo ID
def ad_delete_subject(subject_id):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()

            # Step 1: Get all teachers associated with the subject
            cursor.execute('SELECT TeacherID, TeacherCode FROM Teachers WHERE SubjectID = %s', (subject_id,))
            teachers = cursor.fetchall()
            if teachers:
                for teacher in teachers:
                    teacher_id, teacher_code = teacher
                    # Delete dependent records from Teacher_Class table
                    cursor.execute('DELETE FROM Teacher_Class WHERE TeacherID = %s', (teacher_id,))
                    connection.commit()
                    # Delete dependent records from Users table
                    cursor.execute('DELETE FROM Users WHERE TeacherID = %s', (teacher_id,))
                    connection.commit()
                    # Delete the teacher
                    cursor.execute('DELETE FROM Teachers WHERE TeacherCode = %s', (teacher_code,))
                    connection.commit()

            # Step 2: Delete dependent records from Grades table
            cursor.execute('DELETE FROM Grades WHERE SubjectID = %s', (subject_id,))
            connection.commit()

            # Step 3: Delete the subject from Subjects table
            cursor.execute('DELETE FROM Subjects WHERE SubjectID = %s', (subject_id,))
            connection.commit()

            return True, "Subject and associated teachers deleted successfully."
        except Exception as e:
            print(f"Failed to delete subject: {e}")
            return False, f"Failed to delete subject: {e}"
        finally:
            cursor.close()
            connection.close()
    return False, "Database connection failed."

def get_teachers_by_subject(subject_id):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = '''
                SELECT 
                    t.TeacherID AS id,
                    t.TeacherCode AS code,
                    t.TeacherName AS name,
                    s.SubjectName AS subjectname,
                    t.Email AS email
                FROM Teachers t
                JOIN Subjects s ON t.SubjectID = s.SubjectID
                WHERE t.SubjectID = %s
                ORDER BY t.TeacherID ASC
            '''
            cursor.execute(query, (subject_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Failed to get teachers: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def get_classID_by_name(class_name):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT ClassID FROM Classes WHERE ClassName = %s"
            cursor.execute(query, (class_name,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Trả về ClassID
            else:
                return None
        except Exception as e:
            print(f"Failed to get class ID: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_student_info(student_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    s.StudentName,
                    s.StudentCode,
                    s.Address,
                    c.ClassName
                FROM Students s
                LEFT JOIN Classes c ON s.ClassID = c.ClassID
                WHERE s.StudentCode = %s
            """
            cursor.execute(query, (student_code,))
            result = cursor.fetchone()
            if result:
                return {
                    'StudentName': result['StudentName'],
                    'StudentCode': result['StudentCode'],
                    'Address': result['Address'],
                    'ClassName': result['ClassName']
                }
            return None
        except Error as e:
            print(f"Error fetching student info: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_student_subjects_and_teachers(student_code):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT DISTINCT
                    s.SubjectName,
                    t.TeacherName
                FROM Students st
                JOIN Classes c ON st.ClassID = c.ClassID
                JOIN Teacher_Class tc ON c.ClassID = tc.ClassID
                JOIN Teachers t ON tc.TeacherID = t.TeacherID
                JOIN Subjects s ON t.SubjectID = s.SubjectID
                WHERE st.StudentCode = %s
                ORDER BY s.SubjectName
            """
            cursor.execute(query, (student_code,))
            result = cursor.fetchall()
            if result:
                return result
            return None
        except Error as e:
            print(f"Error fetching student subjects and teachers: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_student_count_by_class(class_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM Students WHERE ClassID = %s"
        cursor.execute(query, (class_id,))
        count = cursor.fetchone()[0]
        return count
    except mysql.connector.Error as err:
        print("Database error:", err)
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def ad_update_subject(subject_id, new_name):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = 'UPDATE Subjects SET SubjectName = %s WHERE SubjectID = %s'
            cursor.execute(query, (new_name, subject_id))
            connection.commit()
            return True
        except Exception as e:
            print(f"Failed to update subject: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False