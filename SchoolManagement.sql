-- 1. Tạo cơ sở dữ liệu
CREATE DATABASE SchoolManagementSystem;
USE SchoolManagementSystem;

-- 2. Tạo bảng Teachers
CREATE TABLE Teachers (
    TeacherID INT AUTO_INCREMENT PRIMARY KEY,
    TeacherName VARCHAR(100),
    Subject VARCHAR(100),
    Email VARCHAR(100)
);

-- 3. Tạo bảng Subjects
CREATE TABLE Subjects (
    SubjectID INT AUTO_INCREMENT PRIMARY KEY,
    SubjectName VARCHAR(100)
);

-- 4. Tạo bảng Classes
CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    ClassName VARCHAR(50),
    TeacherID INT,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
);

-- 5. Tạo bảng Students
CREATE TABLE Students (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    StudentName VARCHAR(100),
    BirthDate DATE,
    ClassID INT,
    Address VARCHAR(255),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

-- 6. Tạo bảng Grades
CREATE TABLE Grades (
    GradeID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT,
    SubjectID INT,
    Score DECIMAL(4,2),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
);

-- 7. Dữ liệu mẫu cho bảng Teachers
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

-- 8. Dữ liệu mẫu cho bảng Subjects
INSERT INTO Subjects (SubjectName) VALUES
('Math'), ('Physics'), ('Chemistry'), ('Biology'), ('English'),
('History'), ('Geography'), ('IT'), ('Literature'), ('PE');

-- 9. Dữ liệu mẫu cho bảng Classes
INSERT INTO Classes (ClassName, TeacherID) VALUES
('10A1', 1), ('10A2', 2), ('10A3', 3), ('10B1', 4), ('10B2', 5),
('11A1', 6), ('11A2', 7), ('11B1', 8), ('11B2', 9), ('12A1', 10);

-- 10. Dữ liệu mẫu cho bảng Students
INSERT INTO Students (StudentName, BirthDate, ClassID, Address) VALUES
('Nguyen Tuan', '2007-03-05', 1, 'Hanoi'),
('Tran Anh', '2007-07-11', 2, 'Hanoi'),
('Le Huyen', '2007-05-22', 3, 'Hai Phong'),
('Pham Nam', '2007-10-01', 4, 'Da Nang'),
('Do Linh', '2007-01-30', 5, 'HCM City'),
('Hoang Long', '2006-09-14', 6, 'Quang Ninh'),
('Bui Thao', '2006-12-25', 7, 'Nghe An'),
('Dang Tuan', '2006-08-07', 8, 'Bac Ninh'),
('Ngo Mai', '2006-04-17', 9, 'Ninh Binh'),
('Pham Duong', '2006-06-18', 10, 'Ha Tinh');

-- 11. Dữ liệu mẫu cho bảng Grades
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

-- 12. Tạo View: Class Roster
CREATE VIEW ClassRoster AS
SELECT s.StudentID, s.StudentName, c.ClassName, t.TeacherName
FROM Students s
JOIN Classes c ON s.ClassID = c.ClassID
JOIN Teachers t ON c.TeacherID = t.TeacherID;

-- 13. Tạo View: Top Students (score >= 8.5)
CREATE VIEW TopStudents AS
SELECT s.StudentID, s.StudentName, sub.SubjectName, g.Score
FROM Grades g
JOIN Students s ON g.StudentID = s.StudentID
JOIN Subjects sub ON g.SubjectID = sub.SubjectID
WHERE g.Score >= 8.5;

-- 14. Tạo Stored Procedure: Add Grade
DELIMITER //

CREATE PROCEDURE AddGrade(
    IN p_StudentID INT,
    IN p_SubjectID INT,
    IN p_Score DECIMAL(4,2)
)
BEGIN
    INSERT INTO Grades (StudentID, SubjectID, Score)
    VALUES (p_StudentID, p_SubjectID, p_Score);
END //

DELIMITER ;

-- 15. Tạo Trigger: Log New Grade
CREATE TABLE GradeLog (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT,
    SubjectID INT,
    Score DECIMAL(4,2),
    InsertedAt DATETIME
);

DELIMITER //

CREATE TRIGGER LogNewGrade
AFTER INSERT ON Grades
FOR EACH ROW
BEGIN
    INSERT INTO GradeLog (StudentID, SubjectID, Score, InsertedAt)
    VALUES (NEW.StudentID, NEW.SubjectID, NEW.Score, NOW());
END //

DELIMITER ;

-- 16. Tạo User-Defined Function: Tính GPA
DELIMITER //

CREATE FUNCTION GetStudentGPA(p_StudentID INT)
RETURNS DECIMAL(4,2)
DETERMINISTIC
BEGIN
    DECLARE avgGPA DECIMAL(4,2);
    SELECT AVG(Score) INTO avgGPA
    FROM Grades
    WHERE StudentID = p_StudentID;
    RETURN avgGPA;
END //

DELIMITER ;

-- 17. Tạo tài khoản người dùng
CREATE USER 'teacher_user'@'localhost' IDENTIFIED BY 'teach123';
CREATE USER 'coordinator_user'@'localhost' IDENTIFIED BY 'coord123';
CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'admin123';

-- 18. Cấp quyền cho người dùng
GRANT SELECT ON SchoolManagementSystem.Students TO 'teacher_user'@'localhost';
GRANT SELECT ON SchoolManagementSystem.Subjects TO 'teacher_user'@'localhost';
GRANT INSERT, UPDATE ON SchoolManagementSystem.Grades TO 'teacher_user'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE ON SchoolManagementSystem.Students TO 'coordinator_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON SchoolManagementSystem.Teachers TO 'coordinator_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON SchoolManagementSystem.Classes TO 'coordinator_user'@'localhost';
GRANT SELECT ON SchoolManagementSystem.Grades TO 'coordinator_user'@'localhost';

GRANT ALL PRIVILEGES ON SchoolManagementSystem.* TO 'admin_user'@'localhost';

-- 19. Áp dụng quyền
FLUSH PRIVILEGES;

Select * from GRADES;