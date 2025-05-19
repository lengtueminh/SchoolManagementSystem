# School Management System

A school management system built with Python, KivyMD for the GUI, and MySQL for the database.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SchoolManagementSystem.git
   cd SchoolManagementSystem
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory

5. Set up MySQL database:
   ```bash
   mysql -u root -p < data/database.sql
   ```

6. Run the application:
   ```bash
   python main.py
   ```

## Default Login Credentials

### Admin
- Username: AD24-0001
- Password: 12345

### Teacher
- Username: GV24-0001
- Password: 12345

### Student
- Username: HS24-0001
- Password: 12345 