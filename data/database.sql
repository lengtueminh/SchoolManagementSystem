DROP DATABASE IF EXISTS SchoolManagementSystem;
CREATE DATABASE SchoolManagementSystem;
USE SchoolManagementSystem;

-- Các bảng đã có:
-- - Teachers: TeacherID, TeacherCode, TeacherName, Subject, Email
-- - Students: StudentID, StudentCode, StudentName, BirthDate, ClassID, Address
-- - Admins : AdminID, AdminName, Email, AdminCode
-- - Users: UserID, UserName, Password, UserType, TeacherID/StudentID
-- - Subjects: SubjectID, SubjectName
-- - Classes: ClassID, ClassName, TeacherID 
-- - Grades: GradeID, SubjectID, StudentID, Score 
-- - Teacher_Class_Subject 

-- Các Stored Procedures đã có:
-- - Add grade with Teacher check (giáo viên chỉ thêm được điểm lớp mình dạy)
-- - Update grade with Teacher check (giáo viên chỉ sửa được điểm lớp mình dạy)
-- - Delete grade with Teacher check (giáo viên chỉ xóa được điểm lớp mình dạy)
-- - Get Students list
-- - Get Teachers list 
-- - Get student's information by ID 
-- - Get student's grades by ID
-- - Admin adds/updates/deletes student 

-- Các Triggers đã có:
-- - Tự động tạo mã học sinh, giáo viên, admin theo dạng "XX24-0001"  

CREATE TABLE Teachers (
    TeacherID INT AUTO_INCREMENT PRIMARY KEY,
    TeacherCode VARCHAR(20) UNIQUE,
    TeacherName VARCHAR(100),
    Subject VARCHAR(100),
    Email VARCHAR(100)
);

CREATE TABLE Admins (
    AdminID INT AUTO_INCREMENT PRIMARY KEY,
    AdminName VARCHAR(100),
    Email VARCHAR(100),
    AdminCode VARCHAR(20) UNIQUE
);

CREATE TABLE Subjects (
    SubjectID INT AUTO_INCREMENT PRIMARY KEY,
    SubjectName VARCHAR(100)
);

CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    ClassName VARCHAR(50),
    TeacherID INT,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
);


CREATE TABLE Students (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    StudentCode VARCHAR(20) UNIQUE,
    StudentName VARCHAR(100),
    BirthDate DATE,
    ClassID INT,
    Address VARCHAR(255),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(100),
    Password VARCHAR(100),
    UserType ENUM('teacher', 'student','admin'),
    TeacherID INT NULL,
    StudentID INT NULL,
    AdminID INT NULL,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (AdminID) REFERENCES Admins(AdminID)
);

CREATE TABLE Grades (
    GradeID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT,
    SubjectID INT,
    Percentage DECIMAL(3,2) CHECK (Percentage IN(0.10, 0.40, 0.50)),
    Score DECIMAL(4,2),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
);

CREATE TABLE Teacher_Class_Subject (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    TeacherID INT,
    ClassID INT,
    SubjectID INT,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID),
    FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
);


-- Trigger: Tự động tạo mã sinh viên dạng "HS24-0001" 
DELIMITER //

CREATE TRIGGER generate_student_code
BEFORE INSERT ON Students
FOR EACH ROW
BEGIN
    DECLARE year_suffix VARCHAR(2);
    DECLARE new_code VARCHAR(20);
    
    SET year_suffix = RIGHT(YEAR(CURDATE()), 2); -- Lấy 2 số cuối của năm hiện tại (ví dụ 24)
    SET new_code = CONCAT('HS', year_suffix, '-', LPAD((SELECT COUNT(*) + 1 FROM Students), 4, '0'));
    
    SET NEW.StudentCode = new_code;
END//

DELIMITER ;


-- Trigger: Tự động tạo mã giáo viên dạng "GV24-0001" 
DELIMITER //

CREATE TRIGGER generate_teacher_code
BEFORE INSERT ON Teachers
FOR EACH ROW
BEGIN
    DECLARE year_suffix VARCHAR(2);
    DECLARE new_code VARCHAR(20);

    SET year_suffix = RIGHT(YEAR(CURDATE()), 2);
    SET new_code = CONCAT('GV', year_suffix, '-', LPAD((SELECT COUNT(*) + 1 FROM Teachers), 4, '0'));

    SET NEW.TeacherCode = new_code;
END//

DELIMITER ;

-- Trigger: Tự động tạo mã Admin dạng "AD24-0001"
DELIMITER //

CREATE TRIGGER generate_admin_code
BEFORE INSERT ON Admins
FOR EACH ROW
BEGIN
    DECLARE year_suffix VARCHAR(2);
    DECLARE new_code VARCHAR(20);

    SET year_suffix = RIGHT(YEAR(CURDATE()), 2);
    SET new_code = CONCAT('AD', year_suffix, '-', LPAD((SELECT COUNT(*) + 1 FROM Admins), 4, '0'));

    SET NEW.AdminCode = new_code;
END//

DELIMITER ;

-- Trigger: Sau khi thêm giáo viên 
DELIMITER //

CREATE TRIGGER after_teacher_insert
AFTER INSERT ON Teachers
FOR EACH ROW
BEGIN
    INSERT INTO Users (Username, Password, UserType, TeacherID)
    VALUES (NEW.TeacherCode, 'default_password', 'teacher', NEW.TeacherID);
END //

DELIMITER ;

-- Trigger: Sau khi thêm học sinh 
DELIMITER //

CREATE TRIGGER after_student_insert
AFTER INSERT ON Students
FOR EACH ROW
BEGIN
    INSERT INTO Users (Username, Password, UserType, StudentID)
    VALUES (NEW.StudentCode, 'default_password', 'student', NEW.StudentID);
END//

DELIMITER ;

-- Add Grade with Teacher Check
DELIMITER //
CREATE PROCEDURE AddGrade(
    IN p_TeacherID INT,
    IN p_StudentID INT,
    IN p_SubjectID INT,
    IN p_Percentage DECIMAL(3,2),
    IN p_Score DECIMAL(4,2)
)
BEGIN
    DECLARE v_ClassID INT;
    DECLARE v_TeacherClassID INT;

    SELECT ClassID INTO v_ClassID FROM Students WHERE StudentID = p_StudentID;
    SELECT TeacherID INTO v_TeacherClassID FROM Classes WHERE ClassID = v_ClassID;

    IF v_TeacherClassID = p_TeacherID THEN
        INSERT INTO Grades (StudentID, SubjectID, Percentage, Score)
        VALUES (p_StudentID, p_SubjectID, p_Percentage, p_Score);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unauthorized: Teacher does not teach this student.';
    END IF;
END //

-- Update Grade with Teacher Check
DELIMITER //
CREATE PROCEDURE UpdateGrade(
    IN p_TeacherID INT,
    IN p_GradeID INT,
    IN p_Score DECIMAL(4,2)
)
BEGIN
    DECLARE v_StudentID INT;
    DECLARE v_ClassID INT;
    DECLARE v_TeacherClassID INT;

    SELECT StudentID INTO v_StudentID FROM Grades WHERE GradeID = p_GradeID;
    SELECT ClassID INTO v_ClassID FROM Students WHERE StudentID = v_StudentID;
    SELECT TeacherID INTO v_TeacherClassID FROM Classes WHERE ClassID = v_ClassID;

    IF v_TeacherClassID = p_TeacherID THEN
        UPDATE Grades SET Score = p_Score WHERE GradeID = p_GradeID;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unauthorized: Teacher cannot update this grade.';
    END IF;
END //
DELIMITER ;

-- Delete Grade with Teacher Check
DELIMITER //
CREATE PROCEDURE DeleteGrade(
    IN p_TeacherID INT,
    IN p_GradeID INT
)
BEGIN
    DECLARE v_StudentID INT;
    DECLARE v_ClassID INT;
    DECLARE v_TeacherClassID INT;

    SELECT StudentID INTO v_StudentID FROM Grades WHERE GradeID = p_GradeID;
    SELECT ClassID INTO v_ClassID FROM Students WHERE StudentID = v_StudentID;
    SELECT TeacherID INTO v_TeacherClassID FROM Classes WHERE ClassID = v_ClassID;

    IF v_TeacherClassID = p_TeacherID THEN
        DELETE FROM Grades WHERE GradeID = p_GradeID;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unauthorized: Teacher cannot delete this grade.';
    END IF;
END //
DELIMITER ;

-- Stored Procedure: Lấy danh sách giáo viên 
DELIMITER //

CREATE PROCEDURE GetTeachers()
BEGIN
    SELECT UserID, Username, UserType
    FROM Users
    WHERE UserType = 'teacher';
END//

DELIMITER ;

-- Stored Procedure: Lấy danh sách học sinh  
DELIMITER //

CREATE PROCEDURE GetStudents()
BEGIN
    SELECT UserID, Username, UserType
    FROM Users
    WHERE UserType = 'student';
END//

DELIMITER ;

-- Get Student Info (by ID)
DELIMITER //
CREATE PROCEDURE GetStudentInfo(
    IN p_StudentID INT
)
BEGIN
    SELECT * FROM Students WHERE StudentID = p_StudentID;
END //
DELIMITER ;

-- Get Student Grades (by ID)
DELIMITER //
CREATE PROCEDURE GetStudentGrades(
    IN p_StudentID INT
)
BEGIN
    SELECT s.SubjectName, g.Score 
    FROM Grades g
    JOIN Subjects s ON g.SubjectID = s.SubjectID
    WHERE g.StudentID = p_StudentID;
END //
DELIMITER ;

-- Admin Add Student
DELIMITER //
CREATE PROCEDURE AdminAddStudent(
    IN p_AdminID INT,
    IN p_StudentName VARCHAR(100),
    IN p_BirthDate DATE,
    IN p_ClassID INT,
    IN p_Address VARCHAR(255)
)
BEGIN
    IF EXISTS (SELECT 1 FROM Admins WHERE AdminID = p_AdminID) THEN
        INSERT INTO Students (StudentName, BirthDate, ClassID, Address)
        VALUES (p_StudentName, p_BirthDate, p_ClassID, p_Address);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Access Denied: Admin only.';
    END IF;
END //
DELIMITER ;

-- Admin Update Student
DELIMITER //
CREATE PROCEDURE AdminUpdateStudent(
    IN p_AdminID INT,
    IN p_StudentID INT,
    IN p_StudentName VARCHAR(100),
    IN p_BirthDate DATE,
    IN p_ClassID INT,
    IN p_Address VARCHAR(255)
)
BEGIN
    IF EXISTS (SELECT 1 FROM Admins WHERE AdminID = p_AdminID) THEN
        UPDATE Students
        SET StudentName = p_StudentName,
            BirthDate = p_BirthDate,
            ClassID = p_ClassID,
            Address = p_Address
        WHERE StudentID = p_StudentID;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Access Denied: Admin only.';
    END IF;
END //
DELIMITER ;

-- Admin Delete Student
DELIMITER //
CREATE PROCEDURE AdminDeleteStudent(
    IN p_AdminID INT,
    IN p_StudentID INT
)
BEGIN
    IF EXISTS (SELECT 1 FROM Admins WHERE AdminID = p_AdminID) THEN
        DELETE FROM Students WHERE StudentID = p_StudentID;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Access Denied: Admin only.';
    END IF;
END //
DELIMITER ;

-- Admin change user's password / users change their password.
DELIMITER //

CREATE PROCEDURE sp_ChangePassword(
    IN p_RequestUserID INT,    
    IN p_TargetUserID INT,     
    IN p_NewPassword VARCHAR(255)
)
BEGIN
    DECLARE v_RequestUserType VARCHAR(50);

    SELECT UserType INTO v_RequestUserType
    FROM Users
    WHERE UserID = p_RequestUserID;

    -- Role checking
    IF v_RequestUserType = 'admin' OR p_RequestUserID = p_TargetUserID THEN
        UPDATE Users
        SET Password = p_NewPassword
        WHERE UserID = p_TargetUserID;
    ELSE
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Permission denied to change password.';
    END IF;
END //

DELIMITER ;

INSERT INTO Teachers (TeacherName, Subject, Email) VALUES
('Nguyen Van A', 'Math', 'a.nguyen@school.edu.vn'),
('Tran Thi B', 'Physics', 'b.tran@school.edu.vn'),
('Le Van C', 'Chemistry', 'c.le@school.edu.vn'),
('Pham Thi D', 'Biology', 'd.pham@school.edu.vn'),
('Do Van E', 'English', 'e.do@school.edu.vn'),
('Hoang Thi F', 'History', 'f.hoang@school.edu.vn'),
('Bui Van G', 'Geography', 'g.bui@school.edu.vn'),
('Dang Thi H', 'IT', 'h.dang@school.edu.vn'),
('Ngo Van I', 'Literature', 'i.ngo@school.edu.vn'),
('Pham Van J', 'PE', 'j.pham@school.edu.vn');

INSERT INTO Subjects (SubjectName) VALUES
('Math'), ('English'), ('History');

INSERT INTO Classes (ClassName, TeacherID) VALUES
('10A1', 1), ('10A2', 2), ('10A3', 3), ('11A1', 6), ('11A2', 7);

INSERT INTO Students (StudentName, BirthDate, ClassID, Address) VALUES
('Nguyen Tuan', '2007-03-05', 1, 'Hanoi'),
('Nguyen Minh', '2007-04-15', 1, 'Hanoi'),
('Tran Khoa', '2007-02-20', 1, 'Hanoi'),
('Pham Lan', '2007-06-11', 1, 'Hanoi'),

('Tran Anh', '2007-07-11', 2, 'Hanoi'),
('Le Giang', '2007-08-08', 2, 'Hung Yen'),
('Vu Anh', '2007-12-12', 2, 'Hung Yen'),
('Bui Quynh', '2007-03-03', 2, 'Ha Nam'),

('Le Huyen', '2007-05-22', 3, 'Hai Phong'),
('Nguyen Ha', '2007-06-30', 3, 'Hai Duong'),
('Phan Linh', '2007-09-09', 3, 'Hai Phong'),
('Doan Phuong', '2007-04-04', 3, 'Nam Dinh'),

('Pham Nam', '2007-10-01', 4, 'Da Nang'),
('Doan Nam', '2007-05-18', 4, 'Hue'),
('Tran Hieu', '2007-11-01', 4, 'Da Nang'),
('Nguyen Hanh', '2007-08-02', 4, 'Da Nang'),

('Do Linh', '2007-01-30', 5, 'HCM City'),
('Ngo Hanh', '2007-03-03', 5, 'Can Tho'),
('Pham Binh', '2007-07-21', 5, 'HCM City'),
('Bui Ngan', '2007-09-19', 5, 'Vung Tau');

INSERT INTO Grades (StudentID, SubjectID, Percentage, Score) VALUES
(1, 1, 0.10, 9.0), (1, 1, 0.40, 7.5), (1, 1, 0.50, 8.0), 
(1, 2, 0.10, 10.0), (1, 2, 0.40, 6.0), (1, 2, 0.50, 7.5), 
(1, 3, 0.10, 10.0), (1, 3, 0.40, 7.5), (1, 3, 0.50, 9.5),

(2, 1, 0.10, 9.5), (2, 1, 0.40, 8.0), (2, 1, 0.50, 9.0), 
(2, 2, 0.10, 10.0), (2, 2, 0.40, 6.5), (2, 2, 0.50, 8.0), 
(2, 3, 0.10, 9.0), (2, 3, 0.40, 9.0), (2, 3, 0.50, 9.0),

(3, 1, 0.10, 9.0), (3, 1, 0.40, 8.5), (3, 1, 0.50, 7.5), 
(3, 2, 0.10, 9.0), (3, 2, 0.40, 8.0), (3, 2, 0.50, 8.0), 
(3, 3, 0.10, 10.0), (3, 3, 0.40, 9.5), (3, 3, 0.50, 9.5),

(4, 1, 0.10, 10.0), (4, 1, 0.40, 7.0), (4, 1, 0.50, 6.5), 
(4, 2, 0.10, 9.0), (4, 2, 0.40, 7.5), (4, 2, 0.50, 8.0), 
(4, 3, 0.10, 10.0), (4, 3, 0.40, 7.0), (4, 3, 0.50, 8.5),

(5, 1, 0.10, 10.0), (5, 1, 0.40, 9.0), (5, 1, 0.50, 8.5), 
(5, 2, 0.10, 10.0), (5, 2, 0.40, 7.5), (5, 2, 0.50, 9.0), 
(5, 3, 0.10, 10.0), (5, 3, 0.40, 8.0), (5, 3, 0.50, 8.5);

INSERT INTO Teacher_Class_Subject (TeacherID, ClassID, SubjectID)
VALUES (1, 2, 3);

select * from Users;
select * from Teacher_Class_Subject;
