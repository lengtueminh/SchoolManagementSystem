DROP DATABASE IF EXISTS SchoolManagementSystem;
CREATE DATABASE SchoolManagementSystem;
USE SchoolManagementSystem;

-- Các bảng đã có:
-- - Subjects: SubjectID, SubjectName
-- - Teachers: TeacherID, TeacherCode, TeacherName, SubjectID, Email
-- - Students: StudentID, StudentCode, StudentName, BirthDate, ClassID, Address
-- - Admins : AdminID, AdminName, Email, AdminCode
-- - Users: UserID, UserName, Password, UserType, TeacherID/StudentID
-- - Classes: ClassID, ClassName 
-- - Grades: GradeID, SubjectID, StudentID, Score 
-- - Teacher_Class: ID, TeacherID, ClassID

-- Các Stored Procedures đã có:
-- - Add grade with Teacher check (giáo viên chỉ thêm được điểm lớp mình dạy) --> CẦN SỬA: Không cần phân quyền 
-- - Update grade with Teacher check (giáo viên chỉ sửa được điểm lớp mình dạy) --> CẦN SỬA: Không cần phân quyền 
-- - Delete grade with Teacher check (giáo viên chỉ xóa được điểm lớp mình dạy) --> CẦN XÓA: Vì không được xóa điểm, chỉ được sửa 
-- - Get Students list
-- - Get Teachers list 
-- - Get student's information by ID 
-- - Get student's grades by student's code 
-- - Get student's GPA by student's code 
-- - Get student's classes by student's code 
-- - Admin adds/updates/deletes student --> CẦN SỬA: Không cần phân quyền 

-- Các Triggers đã có:
-- - Tự động tạo mã học sinh, giáo viên, admin theo dạng "XX24-0001"  
-- - Truy xuất các môn học và giáo viên phụ trách theo StudentID 
-- - TỰ động add user sau khi add gv hoặc hs 

CREATE TABLE Subjects (
    SubjectID INT AUTO_INCREMENT PRIMARY KEY,
    SubjectName VARCHAR(100)
);

CREATE TABLE Teachers (
    TeacherID INT AUTO_INCREMENT PRIMARY KEY,
    TeacherCode VARCHAR(20) UNIQUE,
    TeacherName VARCHAR(100),
    SubjectID INT,
    Email VARCHAR(100),
    FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
);

CREATE TABLE Admins (
    AdminID INT AUTO_INCREMENT PRIMARY KEY,
    AdminName VARCHAR(100),
    Email VARCHAR(100),
    AdminCode VARCHAR(20) UNIQUE
);

CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    ClassName VARCHAR(50)
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

CREATE TABLE Teacher_Class (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    TeacherID INT,
    ClassID INT,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

CREATE TABLE StudentCodeSequence (
    YearPrefix VARCHAR(4), -- e.g., 'HS25'
    LastSequence INT,      -- Last used sequence number for that year
    PRIMARY KEY (YearPrefix)
);
-- Trigger: Tự động tạo mã sinh viên dạng "HS24-0001" 
DELIMITER //
CREATE TRIGGER generate_student_code
BEFORE INSERT ON Students
FOR EACH ROW
BEGIN
    DECLARE year_suffix VARCHAR(2);
    DECLARE year_prefix VARCHAR(4);
    DECLARE new_sequence INT;

    -- Step 1: Get the year prefix (e.g., 'HS25')
    SET year_suffix = RIGHT(YEAR(CURDATE()), 2); -- e.g., '25' for 2025
    SET year_prefix = CONCAT('HS', year_suffix); -- e.g., 'HS25'

    -- Step 2: Atomically increment the sequence number for this year
    INSERT INTO StudentCodeSequence (YearPrefix, LastSequence)
    VALUES (year_prefix, 1)
    ON DUPLICATE KEY UPDATE LastSequence = LastSequence + 1;

    -- Step 3: Get the new sequence number
    SELECT LastSequence INTO new_sequence
    FROM StudentCodeSequence
    WHERE YearPrefix = year_prefix;

    -- Step 4: Generate the StudentCode (e.g., 'HS25-0001')
    SET NEW.StudentCode = CONCAT(year_prefix, '-', LPAD(new_sequence, 4, '0'));
END//
DELIMITER ;

CREATE TABLE TeacherCodeSequence (
    YearPrefix VARCHAR(4),
    LastSequence INT,
    PRIMARY KEY (YearPrefix)
);
-- Trigger: Tự động tạo mã giáo viên dạng "GV24-0001" 
DELIMITER //
CREATE TRIGGER generate_teacher_code
BEFORE INSERT ON Teachers
FOR EACH ROW
BEGIN
    DECLARE year_suffix VARCHAR(2);
    DECLARE year_prefix VARCHAR(4);
    DECLARE new_sequence INT;
    DECLARE new_teacher_code VARCHAR(20);
    DECLARE code_exists INT DEFAULT 1;

    SET year_suffix = RIGHT(YEAR(CURDATE()), 2);
    SET year_prefix = CONCAT('GV', year_suffix);

    -- Insert or update the sequence
    INSERT INTO TeacherCodeSequence (YearPrefix, LastSequence)
    VALUES (year_prefix, 1)
    ON DUPLICATE KEY UPDATE LastSequence = LastSequence + 1;

    -- Get the new sequence
    SELECT LastSequence INTO new_sequence
    FROM TeacherCodeSequence
    WHERE YearPrefix = year_prefix;

    -- Generate and check for unique TeacherCode
    WHILE code_exists > 0 DO
        SET new_teacher_code = CONCAT(year_prefix, '-', LPAD(new_sequence, 4, '0'));
        SELECT COUNT(*) INTO code_exists
        FROM Teachers
        WHERE TeacherCode = new_teacher_code;
        IF code_exists > 0 THEN
            SET new_sequence = new_sequence + 1;
            UPDATE TeacherCodeSequence
            SET LastSequence = new_sequence
            WHERE YearPrefix = year_prefix;
        END IF;
    END WHILE;

    -- Assign the unique TeacherCode to the new row
    SET NEW.TeacherCode = new_teacher_code;
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

-- Trigger: Add user sau khi thêm giáo viên 
DELIMITER //
CREATE TRIGGER after_teacher_insert
AFTER INSERT ON Teachers
FOR EACH ROW
BEGIN
    INSERT INTO Users (Username, Password, UserType, TeacherID)
    VALUES (NEW.TeacherCode, '12345', 'teacher', NEW.TeacherID);
END //
DELIMITER ;

-- Trigger: Add user sau khi thêm admin
DELIMITER //
CREATE TRIGGER after_admin_insert
AFTER INSERT ON Admins
FOR EACH ROW
BEGIN
    INSERT INTO Users (Username, Password, UserType, TeacherID)
    VALUES (NEW.AdminCode, '12345', 'admin', NEW.AdminID);
END //
DELIMITER ;


-- Trigger: Add user sau khi thêm học sinh 
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

-- Delete Grade with Teacher Check --> GRADES SHOULD NOT BE DELETED --> WE SHOULD DELETE THIS SP 
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
    SELECT TeacherID, TeacherCode, TeacherName
    FROM Teachers;
END//
DELIMITER ;

-- Stored Procedure: Lấy danh sách học sinh  
DELIMITER //
CREATE PROCEDURE GetStudents()
BEGIN
    SELECT StudentID, StudentCode, StudentName
    FROM Students;
END//
DELIMITER ;

-- Đang query trực tiếp trong code, check if we should keep this SP or not  
-- Get Student Info (by ID)
-- DELIMITER //
-- CREATE PROCEDURE GetStudentInfo(
--     IN p_StudentID INT
-- )
-- BEGIN
--     SELECT * FROM Students WHERE StudentID = p_StudentID;
-- END //
-- DELIMITER ;


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

-- Admin Delete Student --> SỬA LẠI: KHÔNG CẦN CHECK QUYỀN 
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

-- CHECK THIS
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
-- CHECK ABOVE


-- SP: Get student's classes (subject and its teacher) by student's code (used in Student's screens (Classes))
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


-- SP: Get student's grades by student's code (used in Student's screens (Academic Results)) 
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


-- SP: Get student's GPA by student's code (used in Student's screens (Academic Results)) 
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

INSERT INTO Subjects (SubjectName) VALUES
('Math'),('Science'),('History'),('English'),('Art'),('Music'),('Physical Education'),('Computer Science'),('Foreign Language');

INSERT INTO Teachers (TeacherName, SubjectID, Email) VALUES 
('Jeffy Ortes', 1, 'jortes0@hibu.com'),
('Marianne Teasdale', 2, 'mteasdale1@census.gov'),
('Chanda Strangwood', 3, 'cstrangwood2@skyrock.com'),
('Waneta Clemence', 4, 'wclemence3@disqus.com'),
('Leo Jenkin', 5, 'ljenkin4@networkadvertising.org'),
('Munroe Kment', 6, 'mkment5@hugedomains.com'),
('Sibilla Kybird', 7, 'skybird6@flavors.me'),
('Kristal Yurmanovev', 8, 'kyurmanovev7@who.int'),
('Madelina Bunney', 9, 'mbunney8@usatoday.com'),
('Charlean Corsor', 1, 'ccorsor9@soundcloud.com'),
('Moise Wilsone', 2, 'mwilsonea@unesco.org'),
('Adela Robertsson', 3, 'arobertssonb@buzzfeed.com'),
('Donnie Mockford', 4, 'dmockfordc@reverbnation.com'),
('Nana Mawdsley', 5, 'nmawdsleyd@umich.edu'),
('Tamara Halfacre', 6, 'thalfacree@privacy.gov.au'),
('Jimmy Petrelli', 7, 'jpetrellif@lycos.com'),
('Nickie Waby', 8, 'nwabyg@ycombinator.com'),
('Dallon Piddletown', 9, 'dpiddletownh@sbwire.com'),
('Suki Manicom', 1, 'smanicomi@friendfeed.com'),
('Issie Skirrow', 2, 'iskirrowj@blinklist.com'),
('Hervey Tunnow', 3, 'htunnowk@buzzfeed.com');

INSERT INTO Classes (ClassName) VALUES
('10A1'),('10A2'),('11A1'),('11A2'),('11A3'),('12A1'),('12A2'),('12A3');

INSERT INTO Teacher_Class (TeacherID, ClassID) VALUES
(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1),
(10, 2), (11,2), (12, 2), (13, 2), (14, 2), (15, 2), (16, 2), (17, 2), (18,2),
(19, 3), (20, 3), (21, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3),
(10, 4), (11, 4), (12, 4), (13, 4), (14, 4), (15, 4), (16, 4), (17, 4), (18, 4),
(10, 5), (2, 5), (12, 5), (4, 5), (14, 5), (6, 5), (16, 5), (8, 5), (18, 5),
(1, 6), (11, 6), (3, 6), (13, 6), (5, 6), (15, 6), (7, 6), (17, 6), (9, 6),
(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (15, 7), (16, 7), (17, 7), (18,7),
(10, 8), (11, 8), (12, 8), (13, 8), (14, 8), (6, 8), (7, 8), (8, 8), (9, 8);

INSERT INTO Students (StudentName, BirthDate, ClassID, Address) VALUES
('Tabitha Schoolfield', '2001-02-10', '1', '7873 Robbs Road, Columbus, Georgia, United States, 31914'),
('Staci Gilchrist', '2001-03-25', '1', '2096 Brookhaven Place, Irvine, California, United States, 92710'),
('Vivian Enderby', '2000-08-12', '1', '7772 Clifford Court, Henderson, Nevada, United States, 89012'),
('Udall Gloucester', '2001-04-09', '1', '14519 Netherclift Terrace, Knoxville, Tennessee, United States, 37931'),
('Farris Scrine', '2000-11-30', '1', '9283 Laufersky Lane, Trenton, New Jersey, United States, 08638'),
('Jarid Leander', '2001-04-26', '2', '13282 Kurtz Lane, Norfolk, Virginia, United States, 23509'),
('Phyllis Leeming', '2001-01-31', '2', '11675 August Loop, Philadelphia, Pennsylvania, United States, 19184'),
('Luisa Fliege', '2000-12-23', '2', '12126 Keeley Court, San Jose, California, United States, 95173'),
('Onfre Bugby', '2000-06-02', '2', '1251 Brittany Terrace, Jacksonville, Florida, United States, 32204'),
('Corene Holleran', '2001-05-02', '2', '3797 Began Place, Evansville, Indiana, United States, 47725'),
('Edi Calderbank', '2001-05-05', '3', '6776 Tanner Drive, San Jose, California, United States, 95160'),
('Prentice Slisby', '2001-02-23', '3', '2960 Dalzell Court, Sacramento, California, United States, 95813'),
('Janeva Abry', '2000-08-16', '3', '4905 Hortensia Place, Bradenton, Florida, United States, 34210'),
('Lindsay Hedley', '2001-02-03', '3', '5941 Quary Place, Anchorage, Alaska, United States, 99522'),
('Selle Walling', '2001-03-11', '3', '13213 Westminster Court, Sacramento, California, United States, 94237'),
('Ruperto Cavey', '2001-03-21', '4', '13765 Halyard Court, Santa Monica, California, United States, 90405'),
('Brew Dibnah', '2000-08-30', '4', '4601 Renwick Way, Wilmington, Delaware, United States, 19897'),
('Davon Peepall', '2000-05-21', '4', '13681 Mazzio Lane, Washington, District of Columbia, United States, 20073'),
('Beulah Dronsfield', '2000-08-12', '4', '12502 Brunson Way, Shawnee Mission, Kansas, United States, 66210'),
('Augustus Tomkins', '2001-02-16', '4', '1309 Tinsley Terrace, North Little Rock, Arkansas, United States, 72118'),
('Corbin Clyant', '2000-07-03', '5', '5332 Gallinule Court, Des Moines, Iowa, United States, 50335'),
('Whit Trudgian', '2001-01-22', '5', '3188 Morley Avenue, Lubbock, Texas, United States, 79410'),
('Michel Maase', '2000-09-30', '5', '10593 Almanza Drive, Tampa, Florida, United States, 33673'),
('Moria Ivasechko', '2001-03-19', '5', '4839 Day Lily Run, Hollywood, Florida, United States, 33023'),
('Pavla Kasbye', '2000-07-11', '5', '6265 Pennecamp Drive, Staten Island, New York, United States, 10305'),
('Holt Hoys', '2000-07-05', '6', '7807 Parrot Place, Hartford, Connecticut, United States, 06183'),
('Virge Braid', '2000-07-12', '6', '7318 Halstead Terrace, Des Moines, Iowa, United States, 50936'),
('Janeta Pointing', '2000-08-15', '6', '4494 Baez Way, Biloxi, Mississippi, United States, 39534'),
('Hodge Lowy', '2000-10-04', '6', '3259 Flynn Circle, Cleveland, Ohio, United States, 44118'),
('Aldus Elbourne', '2001-04-15', '6', '10168 Pensacola Place, New York City, New York, United States, 10014'),
('Shanda Kindon', '2000-06-08', '7', '14739 Jonesville Terrace, Wilmington, Delaware, United States, 19886'),
('Anetta Fricker', '2001-02-19', '7', '3161 Mccook Street, Santa Barbara, California, United States, 93111'),
('Michele McAster', '2000-09-11', '7', '5061 Walmer Lane, Charleston, South Carolina, United States, 29424'),
('Steffie Edmondson', '2000-08-31', '7', '14446 Orangeburg Terrace, Warren, Michigan, United States, 48092'),
('Ezra Arnoud', '2000-07-18', '7', '3390 Bowles Place, San Diego, California, United States, 92153'),
('Kilian Paulo', '2000-07-10', '8', '704 Fawnridge Court, Oklahoma City, Oklahoma, United States, 73114'),
('Hayden Galero', '2000-08-01', '8', '7181 Lewisfield Terrace, Boston, Massachusetts, United States, 02298'),
('Sisile Ormston', '2000-08-31', '8', '5673 Palma Drive, Washington, District of Columbia, United States, 20215'),
('Sharla Stone', '2001-02-12', '8', '12132 Callaway Drive, Houston, Texas, United States, 77288'),
('Kakalina Huffy', '2000-12-03', '8', '13942 Heath Springs Drive, Jackson, Mississippi, United States, 39210');

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
(5, 3, 0.10, 10.0), (5, 3, 0.40, 8.0), (5, 3, 0.50, 8.5),

(6, 1, 0.10, 9.0), (6, 1, 0.40, 7.0), (6, 1, 0.50, 7.5), 
(6, 2, 0.10, 8.0), (6, 2, 0.40, 5.5), (6, 2, 0.50, 8.0), 
(6, 3, 0.10, 9.0), (6, 3, 0.40, 6.0), (6, 3, 0.50, 6.5),

(7, 1, 0.10, 9.0), (7, 1, 0.40, 6.0), (7, 1, 0.50, 7.5), 
(7, 2, 0.10, 9.0), (7, 2, 0.40, 7.5), (7, 2, 0.50, 8.0), 
(7, 3, 0.10, 9.0), (7, 3, 0.40, 8.0), (7, 3, 0.50, 9.5),

(8, 1, 0.10, 9.0), (8, 1, 0.40, 7.0), (8, 1, 0.50, 6.5), 
(8, 2, 0.10, 9.0), (8, 2, 0.40, 7.0), (8, 2, 0.50, 9.0), 
(8, 3, 0.10, 10.0), (8, 3, 0.40, 8.0), (8, 3, 0.50, 6.5),

(9, 1, 0.10, 10.0), (9, 1, 0.40, 9.0), (9, 1, 0.50, 8.5), 
(9, 2, 0.10, 9.0), (9, 2, 0.40, 8.0), (9, 2, 0.50, 9.0), 
(9, 3, 0.10, 10.0), (9, 3, 0.40, 8.0), (9, 3, 0.50, 9.5),

(10, 1, 0.10, 9.0), (10, 1, 0.40, 7.0), (10, 1, 0.50, 8.0), 
(10, 2, 0.10, 10.0), (10, 2, 0.40, 6.0), (10, 2, 0.50, 7.5), 
(10, 3, 0.10, 10.0), (10, 3, 0.40, 8.5), (10, 3, 0.50, 9.0),

(11, 1, 0.10, 10.0), (11, 1, 0.40, 8.5), (11, 1, 0.50, 8.0), 
(11, 2, 0.10, 10.0), (11, 2, 0.40, 9.0), (11, 2, 0.50, 8.5), 
(11, 3, 0.10, 10.0), (11, 3, 0.40, 8.5), (11, 3, 0.50, 9.5),

(12, 1, 0.10, 8.0), (12, 1, 0.40, 5.0), (12, 1, 0.50, 7.0), 
(12, 2, 0.10, 9.0), (12, 2, 0.40, 6.5), (12, 2, 0.50, 6.5), 
(12, 3, 0.10, 9.0), (12, 3, 0.40, 5.0), (12, 3, 0.50, 7.0),

(13, 1, 0.10, 9.0), (13, 1, 0.40, 7.5), (13, 1, 0.50, 7.5), 
(13, 2, 0.10, 9.0), (13, 2, 0.40, 6.0), (13, 2, 0.50, 7.0), 
(13, 3, 0.10, 8.0), (13, 3, 0.40, 6.5), (13, 3, 0.50, 4.5),

(16, 1, 0.10, 10.0), (16, 1, 0.40, 9.0), (16, 1, 0.50, 8.5), 
(16, 2, 0.10, 10.0), (16, 2, 0.40, 9.5), (16, 2, 0.50, 8.0), 
(16, 3, 0.10, 9.0), (16, 3, 0.40, 8.5), (16, 3, 0.50, 8.5),

(17, 1, 0.10, 10.0), (17, 1, 0.40, 6.0), (17, 1, 0.50, 7.5), 
(17, 2, 0.10, 9.0), (17, 2, 0.40, 8.5), (17, 2, 0.50, 8.0), 
(17, 3, 0.10, 9.0), (17, 3, 0.40, 8.0), (17, 3, 0.50, 7.5),

(18, 1, 0.10, 10.0), (18, 1, 0.40, 8.0), (18, 1, 0.50, 6.5), 
(18, 2, 0.10, 9.0), (18, 2, 0.40, 8.0), (18, 2, 0.50, 9.0), 
(18, 3, 0.10, 10.0), (18, 3, 0.40, 6.0), (18, 3, 0.50, 6.5),

(21, 1, 0.10, 8.0), (21, 1, 0.40, 6.0), (21, 1, 0.50, 7.0), 
(21, 2, 0.10, 10.0), (21, 2, 0.40, 9.5), (21, 2, 0.50, 10.0), 
(21, 3, 0.10, 9.0), (21, 3, 0.40, 7.0), (21, 3, 0.50, 8.0),

(22, 1, 0.10, 7.0), (22, 1, 0.40, 6.0), (22, 1, 0.50, 5.0), 
(22, 2, 0.10, 8.0), (22, 2, 0.40, 6.5), (22, 2, 0.50, 7.0), 
(22, 3, 0.10, 9.0), (22, 3, 0.40, 8.0), (22, 3, 0.50, 8.0),

(23, 1, 0.10, 9.0), (23, 1, 0.40, 8.0), (23, 1, 0.50, 6.5), 
(23, 2, 0.10, 9.5), (23, 2, 0.40, 9.0), (23, 2, 0.50, 7.0), 
(23, 3, 0.10, 10.0), (23, 3, 0.40, 9.5), (23, 3, 0.50, 7.5),

(26, 1, 0.10, 9.0), (26, 1, 0.40, 7.0), (26, 1, 0.50, 6.5), 
(26, 2, 0.10, 9.0), (26, 2, 0.40, 5.5), (26, 2, 0.50, 6.0), 
(26, 3, 0.10, 8.0), (26, 3, 0.40, 6.5), (26, 3, 0.50, 4.5),

(27, 1, 0.10, 9.0), (27, 1, 0.40, 8.0), (27, 1, 0.50, 8.5), 
(27, 2, 0.10, 9.0), (27, 2, 0.40, 7.5), (27, 2, 0.50, 8.5), 
(27, 3, 0.10, 10.0), (27, 3, 0.40, 7.0), (27, 3, 0.50, 9.5),

(28, 1, 0.10, 10.0), (28, 1, 0.40, 9.0), (28, 1, 0.50, 7.5), 
(28, 2, 0.10, 9.0), (28, 2, 0.40, 8.0), (28, 2, 0.50, 9.0), 
(28, 3, 0.10, 10.0), (28, 3, 0.40, 7.0), (28, 3, 0.50, 8.5),

(31, 1, 0.10, 9.0), (31, 1, 0.40, 7.5), (31, 1, 0.50, 8.5), 
(31, 2, 0.10, 10.0), (31, 2, 0.40, 8.0), (31, 2, 0.50, 7.5), 
(31, 3, 0.10, 9.0), (31, 3, 0.40, 8.5), (31, 3, 0.50, 9.5),

(32, 1, 0.10, 9.5), (32, 1, 0.40, 9.0), (32, 1, 0.50, 9.0), 
(32, 2, 0.10, 10.0), (32, 2, 0.40, 9.5), (32, 2, 0.50, 8.0), 
(32, 3, 0.10, 9.0), (32, 3, 0.40, 9.0), (32, 3, 0.50, 10.0),

(33, 1, 0.10, 9.0), (33, 1, 0.40, 4.5), (33, 1, 0.50, 6.5), 
(33, 2, 0.10, 9.0), (33, 2, 0.40, 7.0), (33, 2, 0.50, 6.0), 
(33, 3, 0.10, 10.0), (33, 3, 0.40, 8.5), (33, 3, 0.50, 5.5),

(37, 1, 0.10, 10.0), (37, 1, 0.40, 6.0), (37, 1, 0.50, 7.5), 
(37, 2, 0.10, 9.0), (37, 2, 0.40, 7.5), (37, 2, 0.50, 9.0), 
(37, 3, 0.10, 9.0), (37, 3, 0.40, 8.0), (37, 3, 0.50, 7.5),

(38, 1, 0.10, 9.0), (38, 1, 0.40, 7.0), (38, 1, 0.50, 9.5), 
(38, 2, 0.10, 9.0), (38, 2, 0.40, 8.0), (38, 2, 0.50, 9.0), 
(38, 3, 0.10, 10.0), (38, 3, 0.40, 8.0), (38, 3, 0.50, 8.5),

(39, 1, 0.10, 10.0), (39, 1, 0.40, 9.0), (39, 1, 0.50, 9.5), 
(39, 2, 0.10, 10.0), (39, 2, 0.40, 10.0), (39, 2, 0.50, 9.0), 
(39, 3, 0.10, 10.0), (39, 3, 0.40, 8.5), (39, 3, 0.50, 9.5);

INSERT INTO Admins (AdminName, Email) VALUES
('Marget Evans', 'marget.evans@gmail.com'),
('Rutter Benka', 'rutter.benka@yahoo.com'),
('Rudie O'' Ronan', 'rudie.oronan@yahoo.com'),
('Alia Steffan', 'alia.steffan@hotmail.fr');

SELECT t.Teacherid, t.Teachercode, t.Teachername, t.Email
            FROM Teachers t
            WHERE t.SubjectID = 1;
            
select * from Admins;
            SELECT 
                s.StudentID AS id,
                s.StudentCode AS code,
                s.StudentName AS name,
                s.BirthDate AS birthdate,
                c.ClassName AS classname,
                s.Address AS address
            FROM Students s
            JOIN Classes c ON s.ClassID = c.ClassID
            WHERE s.ClassID = 4;
select * from Students where StudentID = 43;
select * from Subjects;