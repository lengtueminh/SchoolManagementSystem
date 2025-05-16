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

def submit_grade_to_db(teacher_code, student_code, grade, percentage):
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()

            cursor.callproc("AddGradeByTeacherCode", (teacher_code, student_code, percentage, grade))
            connection.commit()
            return True
        except Error as e:
            print(f"Error submitting grade: {e}")
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
    """
    return fetch_all(query)

def get_all_classes():
    query = """
        SELECT 
            ClassID AS id,
            ClassName AS classname
        FROM Classes
    """
    return fetch_all(query)

def get_all_subjects():
    query = """
        SELECT 
            SubjectID AS subjectid,
            SubjectName AS subjectname
        FROM Subjects
    """
    return fetch_all(query)

def get_students_of_class(class_id):
    if class_id:
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
            WHERE s.ClassID = %s
        """
        return fetch_all(query, (class_id,))
    return []

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
            query = """
                UPDATE Teachers
                SET TeacherName = %s, SubjectID = %s, Email = %s,
                WHERE TeacherCode = %s
            """
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
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Students (name, address, birthdate, class_id)
            VALUES (?, ?, ?, ?)
        ''', (name, address, birthdate, class_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to add student: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Thêm giáo viên mới (không tạo mã, mã do DB tự động tạo)
def ad_add_teacher(name, subject_id, email):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Teachers (name, subject_id, email)
            VALUES (?, ?, ?)
        ''', (name, subject_id, email))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to add teacher: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Thêm lớp học mới
def ad_add_class(classname):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Classes (classname)
            VALUES (?)
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
            INSERT INTO Subjects (subjectname)
            VALUES (?)
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
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM Students WHERE code = ?
        ''', (student_code,))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Failed to delete student: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Xóa giáo viên theo mã
def ad_delete_teacher(teacher_code):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM Teachers WHERE code = ?
        ''', (teacher_code,))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Failed to delete teacher: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Xóa lớp học theo ID
def ad_delete_class(class_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM Classes WHERE id = ?
        ''', (class_id,))
        
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
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM Subjects WHERE subjectid = ?
        ''', (subject_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Failed to delete subject: {e}")
        return False
    finally:
        cursor.close()
        conn.close()