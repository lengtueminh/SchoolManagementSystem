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
    UserID INT PRIMARY KEY,
    Username VARCHAR(100),
    Password VARCHAR(100),
    UserType ENUM('teacher', 'student'),
    TeacherID INT NULL,
    StudentID INT NULL,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
);

CREATE TABLE Grades (
    GradeID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT,
    SubjectID INT,
    Score DECIMAL(4,2),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
);

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
('Math'), ('Physics'), ('Chemistry'), ('Biology'), ('English'),
('History'), ('Geography'), ('IT'), ('Literature'), ('PE');

INSERT INTO Classes (ClassName, TeacherID) VALUES
('10A1', 1), ('10A2', 2), ('10A3', 3), ('10B1', 4), ('10B2', 5),
('11A1', 6), ('11A2', 7), ('11B1', 8), ('11B2', 9), ('12A1', 10);

INSERT INTO Students (StudentName, BirthDate, ClassID, Address) VALUES
('Nguyen Tuan', '2007-03-05', 1, 'Hanoi'),
('Nguyen Minh', '2007-04-15', 1, 'Hanoi'),
('Tran Khoa', '2007-02-20', 1, 'Hanoi'),
('Pham Lan', '2007-06-11', 1, 'Hanoi'),
('Hoang Binh', '2007-09-01', 1, 'Hanoi'),

('Tran Anh', '2007-07-11', 2, 'Hanoi'),
('Le Giang', '2007-08-08', 2, 'Hung Yen'),
('Vu Anh', '2007-12-12', 2, 'Hung Yen'),
('Bui Quynh', '2007-03-03', 2, 'Ha Nam'),
('Ngo Khanh', '2007-05-05', 2, 'Thai Binh'),

('Le Huyen', '2007-05-22', 3, 'Hai Phong'),
('Nguyen Ha', '2007-06-30', 3, 'Hai Duong'),
('Phan Linh', '2007-09-09', 3, 'Hai Phong'),
('Doan Phuong', '2007-04-04', 3, 'Nam Dinh'),
('Tran Trang', '2007-10-10', 3, 'Haiphong'),

('Pham Nam', '2007-10-01', 4, 'Da Nang'),
('Doan Nam', '2007-05-18', 4, 'Hue'),
('Tran Hieu', '2007-11-01', 4, 'Da Nang'),
('Nguyen Hanh', '2007-08-02', 4, 'Da Nang'),
('Ngo Bao', '2007-12-21', 4, 'Hue'),

('Do Linh', '2007-01-30', 5, 'HCM City'),
('Ngo Hanh', '2007-03-03', 5, 'Can Tho'),
('Pham Binh', '2007-07-21', 5, 'HCM City'),
('Bui Ngan', '2007-09-19', 5, 'Vung Tau'),
('Tran Tien', '2007-11-11', 5, 'Binh Duong'),

('Hoang Long', '2006-09-14', 6, 'Quang Ninh'),
('Mai Lan', '2006-10-10', 6, 'Quang Ninh'),
('Hoang Hieu', '2006-03-29', 6, 'Hai Phong'),
('Le Tuan', '2006-01-01', 6, 'Quang Ninh'),
('Tran Hoa', '2006-12-12', 6, 'Bac Kan'),

('Bui Thao', '2006-12-25', 7, 'Nghe An'),
('Nguyen Chi', '2006-11-11', 7, 'Nghe An'),
('Vu Trang', '2006-07-07', 7, 'Thanh Hoa'),
('Dang Hoa', '2006-02-02', 7, 'Nghe An'),
('Pham Son', '2006-04-04', 7, 'Ha Tinh'),

('Dang Tuan', '2006-08-07', 8, 'Bac Ninh'),
('Bui Minh', '2006-02-02', 8, 'Bac Ninh'),
('Dang Chau', '2006-06-06', 8, 'Bac Giang'),
('Tran Huy', '2006-09-09', 8, 'Bac Ninh'),
('Nguyen Huan', '2006-05-05', 8, 'Lang Son'),

('Ngo Mai', '2006-04-17', 9, 'Ninh Binh'),
('Le Dung', '2006-01-01', 9, 'Hoa Binh'),
('Pham Linh', '2006-05-05', 9, 'Hoa Binh'),
('Nguyen Nhat', '2006-07-07', 9, 'Ha Nam'),
('Tran Binh', '2006-06-06', 9, 'Ninh Binh'),

('Pham Duong', '2006-06-18', 10, 'Ha Tinh'),
('Tran Hoang', '2006-08-08', 10, 'Ha Tinh'),
('Ngo Thanh', '2006-09-09', 10, 'Quang Tri'),
('Le Yen', '2006-03-03', 10, 'Quang Binh'),
('Bui Duy', '2006-11-11', 10, 'Ha Tinh');

INSERT INTO Grades (StudentID, SubjectID, Score) VALUES
(1, 1, 8.5), (1, 2, 7.5),
(2, 1, 9.0), (2, 3, 6.5),
(3, 2, 8.0), (3, 4, 7.0),
(4, 5, 6.0), (4, 1, 7.5),
(5, 2, 8.8), (5, 3, 9.0),
(6, 4, 6.5), (6, 5, 7.5),
(7, 1, 8.0), (7, 2, 8.5),
(8, 3, 9.0), (8, 4, 7.0),
(9, 5, 6.0), (9, 1, 7.8),
(10, 2, 8.5), (10, 3, 8.0);

-- Add Grade with Teacher Check
DELIMITER //
CREATE PROCEDURE AddGrade(
    IN p_TeacherID INT,
    IN p_StudentID INT,
    IN p_SubjectID INT,
    IN p_Score DECIMAL(4,2)
)
BEGIN
    DECLARE v_ClassID INT;
    DECLARE v_TeacherClassID INT;

    SELECT ClassID INTO v_ClassID FROM Students WHERE StudentID = p_StudentID;
    SELECT TeacherID INTO v_TeacherClassID FROM Classes WHERE ClassID = v_ClassID;

    IF v_TeacherClassID = p_TeacherID THEN
        INSERT INTO Grades (StudentID, SubjectID, Score)
        VALUES (p_StudentID, p_SubjectID, p_Score);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unauthorized: Teacher does not teach this student.';
    END IF;
END //
DELIMITER ;

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

-- Trigger: Sau khi thêm giáo viên 
DELIMITER //

CREATE TRIGGER after_teacher_insert
AFTER INSERT ON Teachers
FOR EACH ROW
BEGIN
    INSERT INTO Users (UserID, Username, Password, UserType, TeacherID)
    VALUES (NEW.TeacherID, NEW.TeacherName, 'default_password', 'teacher', NEW.TeacherID);
END //

DELIMITER ;

-- Trigger: Sau khi thêm học sinh 
DELIMITER 

CREATE TRIGGER after_student_insert
AFTER INSERT ON Students
FOR EACH ROW
BEGIN
    INSERT INTO Users (UserID, Username, Password, UserType, StudentID)
    VALUES (NEW.StudentID, NEW.StudentName, 'default_password', 'student', NEW.StudentID);
END//

DELIMITER ;

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



