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
-- - Truy xuất các môn học và giáo viên phụ trách theo StudentID 

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
    VALUES (NEW.TeacherCode, '12345', 'teacher', NEW.TeacherID);
END //

DELIMITER ;

-- Trigger: Sau khi thêm học sinh 
DELIMITER //

CREATE TRIGGER after_student_insert
AFTER INSERT ON Students
FOR EACH ROW
BEGIN
    INSERT INTO Users (Username, Password, UserType, StudentID)
    VALUES (NEW.StudentCode, '12345', 'student', NEW.StudentID);
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

insert into Teachers (TeacherName, Subject, Email) values ('Jeffy Ortes', 'Physical Education', 'jortes0@hibu.com');
insert into Teachers (TeacherName, Subject, Email) values ('Marianne Teasdale', 'Physical Education', 'mteasdale1@census.gov');
insert into Teachers (TeacherName, Subject, Email) values ('Chanda Strangwood', 'Math', 'cstrangwood2@skyrock.com');
insert into Teachers (TeacherName, Subject, Email) values ('Waneta Clemence', 'Foreign Language', 'wclemence3@disqus.com');
insert into Teachers (TeacherName, Subject, Email) values ('Leo Jenkin', 'Art', 'ljenkin4@networkadvertising.org');
insert into Teachers (TeacherName, Subject, Email) values ('Munroe Kment', 'Foreign Language', 'mkment5@hugedomains.com');
insert into Teachers (TeacherName, Subject, Email) values ('Sibilla Kybird', 'Physical Education', 'skybird6@flavors.me');
insert into Teachers (TeacherName, Subject, Email) values ('Kristal Yurmanovev', 'Computer Science', 'kyurmanovev7@who.int');
insert into Teachers (TeacherName, Subject, Email) values ('Madelina Bunney', 'Math', 'mbunney8@usatoday.com');
insert into Teachers (TeacherName, Subject, Email) values ('Charlean Corsor', 'Art', 'ccorsor9@soundcloud.com');
insert into Teachers (TeacherName, Subject, Email) values ('Moise Wilsone', 'Science', 'mwilsonea@unesco.org');
insert into Teachers (TeacherName, Subject, Email) values ('Adela Robertsson', 'Math', 'arobertssonb@buzzfeed.com');
insert into Teachers (TeacherName, Subject, Email) values ('Donnie Mockford', 'Art', 'dmockfordc@reverbnation.com');
insert into Teachers (TeacherName, Subject, Email) values ('Nana Mawdsley', 'Foreign Language', 'nmawdsleyd@umich.edu');
insert into Teachers (TeacherName, Subject, Email) values ('Tamara Halfacre', 'Science', 'thalfacree@privacy.gov.au');
insert into Teachers (TeacherName, Subject, Email) values ('Jimmy Petrelli', 'Music', 'jpetrellif@lycos.com');
insert into Teachers (TeacherName, Subject, Email) values ('Nickie Waby', 'Computer Science', 'nwabyg@ycombinator.com');
insert into Teachers (TeacherName, Subject, Email) values ('Dallon Piddletown', 'Science', 'dpiddletownh@sbwire.com');
insert into Teachers (TeacherName, Subject, Email) values ('Suki Manicom', 'Science', 'smanicomi@friendfeed.com');
insert into Teachers (TeacherName, Subject, Email) values ('Issie Skirrow', 'Art', 'iskirrowj@blinklist.com');
insert into Teachers (TeacherName, Subject, Email) values ('Hervey Tunnow', 'Physical Education', 'htunnowk@buzzfeed.com');


INSERT INTO Subjects (SubjectName) VALUES
('Math'),
('Science'),
('History'),
('English'),
('Art'),
('Music'),
('Physical Education'),
('Computer Science'),
('Foreign Language'),
('Health');


INSERT INTO Classes (ClassName, TeacherID) VALUES
('10A1', 5),
('11A1', 9),
('12A1', 11),
('10A2', 20),
('11A2', 1),
('12A2', 10),
('10A3', 2),
('11A3', 19),
('12A3', 18),
('10A4', 7),
('11A4', 12),
('12A4', 15);


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
('Bui Ngan', '2007-09-19', 5, 'Vung Tau'),

('Hoàng Thành Đạt', '2006-04-03', 12, 'Hanoi'),
('Bùi Minh Đạt', '2007-03-29', 6, 'Hanoi'),
('Ngô Huy Đạt', '2006-10-23', 9, 'Hanoi'),
('Nguyễn Ngọc Đạt', '2008-09-24', 7, 'Hanoi'),
('Ngô Anh Đạt', '2008-01-04', 12, 'Hanoi'),
('Đỗ Văn Hùng', '2007-05-14', 6, 'Hanoi'),
('Đỗ Tuấn Hùng', '2006-04-03', 8, 'Hanoi'),
('Phạm Hữu Hùng', '2006-08-10', 5, 'Hanoi'),
('Nguyễn Quốc Hùng', '2006-12-26', 10, 'Hanoi'),
('Dương Chí Hùng', '2006-04-08', 3, 'Hanoi'),
('Hồ Minh Khang', '2008-10-29', 8, 'Hanoi'),
('Trần Tuấn Khang', '2006-02-02', 5, 'Hanoi'),
('Phạm Đức Khang', '2007-06-22', 12, 'Hanoi'),
('Dương Hải Khang', '2008-06-05', 4, 'Hanoi'),
('Bùi Trí Khang', '2007-03-22', 9, 'Hanoi'),
('Trần Hoàng Sơn', '2006-11-15', 12, 'Hanoi'),
('Dương Hữu Sơn', '2006-10-14', 7, 'Hanoi'),
('Trần Minh Sơn', '2006-09-10', 12, 'Hanoi'),
('Dương Tuấn Sơn', '2007-09-06', 7, 'Hanoi'),
('Nguyễn Đức Sơn', '2006-02-12', 4, 'Hanoi'),

('Ngô Thành Linh', '2007-09-10', 10, 'Hanoi'),
('Đỗ Huy Linh', '2008-10-05', 10, 'Hanoi'),
('Vũ Văn Linh', '2008-10-16', 6, 'Hanoi'),
('Phan Tuấn Linh', '2006-11-02', 6, 'Hanoi'),
('Vũ Hoàng Linh', '2007-06-26', 6, 'Hanoi'),
('Bùi Quang Linh', '2008-02-14', 9, 'Hanoi'),
('Lê Hải Lâm', '2008-10-21', 8, 'Hanoi'),
('Bùi Văn Lâm', '2007-01-01', 11, 'Hanoi'),
('Phạm Huy Lâm', '2008-07-04', 9, 'Hanoi'),
('Hồ Bảo Lâm', '2006-07-19', 6, 'Hanoi'),
('Ngô Thanh Lâm', '2006-08-18', 5, 'Hanoi'),
('Bùi Minh Lâm', '2008-02-21', 8, 'Hanoi'),
('Hoàng Bảo Nam', '2006-08-25', 10, 'Hanoi'),
('Lê Huy Nam', '2006-05-11', 11, 'Hanoi'),
('Đỗ Hải Nam', '2006-04-11', 1, 'Hanoi'),
('Hồ Thanh Nam', '2007-11-27', 7, 'Hanoi'),
('Bùi Bá Nam', '2007-05-08', 8, 'Hanoi'),
('Vũ Quốc Nam', '2006-09-03', 7, 'Hanoi'),
('Phan Đức Phúc', '2007-03-07', 11, 'Hanoi'),
('Lê Huy Phúc', '2008-04-01', 5, 'Hanoi'),
('Trần Tuấn Phúc', '2006-06-13', 10, 'Hanoi'),
('Đặng Bảo Phúc', '2007-12-25', 12, 'Hanoi'),
('Lê Mạnh Phúc', '2008-09-24', 6, 'Hanoi'),
('Vũ Chấn Phong', '2006-08-24', 9, 'Hanoi'),
('Đỗ Hải Phong', '2008-05-23', 8, 'Hanoi'),
('Ngô Mạnh Phong', '2006-12-08', 12, 'Hanoi'),
('Hồ Quốc Phong', '2008-08-02', 10, 'Hanoi'),
('Nguyễn Thanh Nguyên', '2008-04-06', 11, 'Hanoi'),
('Hồ Trọng Nguyên', '2008-02-08', 9, 'Hanoi'),
('Đỗ Gia Nguyên', '2008-03-25', 8, 'Hanoi'),
('Ngô Trí Nguyên', '2008-11-24', 7, 'Hanoi'),
('Đặng Mạnh Nguyên', '2008-06-26', 12, 'Hanoi'),
('Vũ Bảo Long', '2006-09-14', 7, 'Hanoi'),
('Phan Quốc Long', '2007-09-02', 11, 'Hanoi'),
('Đỗ Huy Long', '2007-10-05', 6, 'Hanoi'),
('Vũ Gia Long', '2008-04-22', 9, 'Hanoi'),
('Vũ Thành Long', '2007-08-09', 6, 'Hanoi'),
('Đỗ Bá Long', '2008-12-04', 10, 'Hanoi');



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

INSERT INTO Teacher_Class_Subject (TeacherID, ClassID, SubjectID) VALUES
-- Giáo viên Toán
(1, 6, 1), (1, 2, 1), (1, 8, 1),
-- Giáo viên Ngữ Văn
(2, 6, 2), (2, 9, 2),
-- Giáo viên Tiếng Anh
(3, 2, 3), (3, 11, 3),
-- Giáo viên Lịch sử
(4, 8, 4), (4, 12, 4),
-- Giáo viên Địa lý
(5, 6, 5), (5, 7, 5),
-- Giáo viên Thể dục
(6, 10, 7), (6, 11, 7),
-- Giáo viên Tin học
(7, 9, 8), (7, 12, 8),
-- Giáo viên Âm nhạc
(8, 7, 6), (8, 8, 6),
-- Giáo viên Sinh học
(9, 10, 9), (9, 11, 9),
-- Giáo viên Ngoại ngữ 2
(10, 6, 10), (10, 12, 10),

-- Một số giáo viên phụ trách nhiều lớp cùng môn
(11, 9, 1), (11, 10, 1),
(12, 11, 2), (12, 12, 2),
(13, 6, 3), (13, 8, 3),
(14, 7, 4), (14, 9, 4),
(15, 10, 5), (15, 12, 5),

-- Một số giáo viên kiêm nhiệm hoặc thay thế
(16, 11, 6),
(17, 7, 7),
(18, 8, 8),
(19, 9, 9),
(20, 10, 10),
(21, 12, 1);

DELIMITER //

DELIMITER //

CREATE PROCEDURE GetSubjectsAndTeachersFromCode(IN inputStudentCode VARCHAR(20))
BEGIN
    DECLARE sid INT;

    -- Lấy StudentID từ StudentCode
    SELECT StudentID INTO sid
    FROM Students
    WHERE StudentCode = inputStudentCode;

    -- Truy xuất môn học và giáo viên từ StudentID
    SELECT 
        s.SubjectName,
        t.TeacherName
    FROM Students st
    JOIN Classes c ON st.ClassID = c.ClassID
    JOIN Teacher_Class_Subject tcs ON c.ClassID = tcs.ClassID
    JOIN Teachers t ON tcs.TeacherID = t.TeacherID
    JOIN Subjects s ON tcs.SubjectID = s.SubjectID
    WHERE st.StudentID = sid;
END//

DELIMITER ;


CALL GetSubjectsAndTeachersFromCode('HS25-0005');

-- select * from Students;

-- DELIMITER //

-- CREATE PROCEDURE GetSubjectsAndTeachersByStudentID(IN inputStudentID INT)
-- BEGIN
--     SELECT 
--         s.SubjectName,
--         t.TeacherName
--     FROM Students AS st
--     JOIN Classes AS c ON st.ClassID = c.ClassID
--     JOIN Teacher_Class_Subject AS tcs ON c.ClassID = tcs.ClassID
--     JOIN Teachers AS t ON tcs.TeacherID = t.TeacherID
--     JOIN Subjects AS s ON tcs.SubjectID = s.SubjectID
--     WHERE st.StudentID = inputStudentID;
-- END//

-- DELIMITER ;

-- CALL GetSubjectsAndTeachersByStudentID(5);

-- select * from Students;



DELIMITER //

CREATE PROCEDURE GetStudentSubjectsGradesByCode(IN p_StudentCode VARCHAR(20))
BEGIN
    DECLARE v_StudentID INT;

    -- Lấy StudentID từ mã sinh viên
    SELECT StudentID INTO v_StudentID
    FROM Students
    WHERE StudentCode = p_StudentCode;

    -- Truy xuất điểm theo môn học, gồm các thành phần và GPA từng môn
    SELECT 
        s.SubjectName,
        MAX(CASE WHEN g.Percentage = 0.10 THEN g.Score END) AS Score_10,
        MAX(CASE WHEN g.Percentage = 0.40 THEN g.Score END) AS Score_40,
        MAX(CASE WHEN g.Percentage = 0.50 THEN g.Score END) AS Score_50,
        ROUND(SUM(g.Score * g.Percentage), 2) AS GPA_Subject
    FROM Grades g
    JOIN Subjects s ON g.SubjectID = s.SubjectID
    WHERE g.StudentID = v_StudentID
    GROUP BY s.SubjectName;

END//

DELIMITER ;

DELIMITER //

CREATE PROCEDURE GetStudentGPAByCode(IN p_StudentCode VARCHAR(20))
BEGIN
    DECLARE v_StudentID INT;

    -- Lấy StudentID từ mã sinh viên
    SELECT StudentID INTO v_StudentID
    FROM Students
    WHERE StudentCode = p_StudentCode;

    -- Truy xuất điểm theo môn học, gồm các thành phần và GPA từng môn
    SELECT 
        s.SubjectName,
        MAX(CASE WHEN g.Percentage = 0.10 THEN g.Score END) AS Score_10,
        MAX(CASE WHEN g.Percentage = 0.40 THEN g.Score END) AS Score_40,
        MAX(CASE WHEN g.Percentage = 0.50 THEN g.Score END) AS Score_50,
        ROUND(SUM(g.Score * g.Percentage), 2) AS GPA_Subject
    FROM Grades g
    JOIN Subjects s ON g.SubjectID = s.SubjectID
    WHERE g.StudentID = v_StudentID
    GROUP BY s.SubjectName;

    -- Trả về GPA chung của học sinh
    SELECT 
        ROUND(SUM(g.Score * g.Percentage) / COUNT(DISTINCT g.SubjectID), 2) AS GPA_Total
    FROM Grades g
    WHERE g.StudentID = v_StudentID;
END//

DELIMITER ;


CALL GetStudentGPAByCode('HS25-0005');