import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="thuhangtran128", 
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
            query = "SELECT TeacherName, Email FROM Teachers WHERE TeacherCode = %s"
            cursor.execute(query, (teacher_code,))
            result = cursor.fetchone()
            if result:
                return {
                    "teacher_name": result[0],
                    "email": result[1]
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
                SELECT ClassName 
                FROM Classes
                WHERE TeacherCode = %s
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
