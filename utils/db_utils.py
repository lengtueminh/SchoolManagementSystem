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
