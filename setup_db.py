from app import app
from models import db
from sqlalchemy import text

def setup():
    # CORRECTED SQL Script (Fixed spaces and typos from PDF)
    sql_script = """
    SET FOREIGN_KEY_CHECKS = 0;
    
    -- DROP TABLES
    DROP TABLE IF EXISTS Timetable;
    DROP TABLE IF EXISTS Feedback;
    DROP TABLE IF EXISTS RequestDocument;
    DROP TABLE IF EXISTS PaymentDocument;
    DROP TABLE IF EXISTS SubmissionDocument;
    DROP TABLE IF EXISTS AssignmentDocument;
    DROP TABLE IF EXISTS CourseDocument;
    DROP TABLE IF EXISTS Document;
    DROP TABLE IF EXISTS AnnouncementDepartment;
    DROP TABLE IF EXISTS AnnouncementCourse;
    DROP TABLE IF EXISTS Announcement;
    DROP TABLE IF EXISTS PaymentAudit;
    DROP TABLE IF EXISTS Payment;
    DROP TABLE IF EXISTS Request;
    DROP TABLE IF EXISTS Attendance;
    DROP TABLE IF EXISTS ExamEvaluation;
    DROP TABLE IF EXISTS ExamResult;
    DROP TABLE IF EXISTS Exam;
    DROP TABLE IF EXISTS SubmissionEvaluation;
    DROP TABLE IF EXISTS Submission;
    DROP TABLE IF EXISTS Assignment;
    DROP TABLE IF EXISTS Prerequisite;
    DROP TABLE IF EXISTS Enrollment;
    DROP TABLE IF EXISTS Teaches;
    DROP TABLE IF EXISTS Course;
    DROP TABLE IF EXISTS Admin;
    DROP TABLE IF EXISTS Faculty;
    DROP TABLE IF EXISTS Student;
    DROP TABLE IF EXISTS Program;
    DROP TABLE IF EXISTS Department;
    DROP TABLE IF EXISTS Person;
    
    SET FOREIGN_KEY_CHECKS = 1;

    -- 1. CORE TABLES
    CREATE TABLE Person (
        PersonID INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        DOB DATE,
        Gender CHAR(1),
        Email VARCHAR(120) UNIQUE NOT NULL,
        Phone VARCHAR(20),
        Address VARCHAR(255),
        Password VARCHAR(255) NOT NULL, 
        Role ENUM('Student','Faculty','Admin') NOT NULL
    );

    CREATE TABLE Department (
        DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
        DeptCode VARCHAR(20) UNIQUE NOT NULL,
        DeptName VARCHAR(100) NOT NULL
    );

    CREATE TABLE Program (
        ProgramID INT AUTO_INCREMENT PRIMARY KEY,
        ProgramCode VARCHAR(20) UNIQUE NOT NULL,
        ProgramName VARCHAR(100) NOT NULL,
        DepartmentID INT NOT NULL,
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    );

    -- 2. ROLES
    CREATE TABLE Student (
        StudentID INT PRIMARY KEY,
        RollNo VARCHAR(30) UNIQUE NOT NULL,
        ProgramID INT NOT NULL,
        Semester INT NOT NULL,
        AdmissionYear INT NOT NULL,
        FOREIGN KEY (StudentID) REFERENCES Person(PersonID),
        FOREIGN KEY (ProgramID) REFERENCES Program(ProgramID)
    );

    CREATE TABLE Faculty (
        FacultyID INT PRIMARY KEY,
        Designation VARCHAR(60),
        DepartmentID INT NOT NULL,
        Qualification VARCHAR(120),
        FOREIGN KEY (FacultyID) REFERENCES Person(PersonID),
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    );

    CREATE TABLE Admin (
        AdminID INT PRIMARY KEY,
        RoleType ENUM('SuperAdmin','DeptAdmin','FinanceAdmin') NOT NULL,
        FOREIGN KEY (AdminID) REFERENCES Person(PersonID)
    );

    -- 3. ACADEMICS
    CREATE TABLE Course (
        CourseID INT AUTO_INCREMENT PRIMARY KEY,
        CourseName VARCHAR(120) NOT NULL,
        Credits INT NOT NULL,
        DepartmentID INT NOT NULL,
        Semester INT NOT NULL,
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    );

    CREATE TABLE Teaches (
        FacultyID INT NOT NULL,
        CourseID INT NOT NULL,
        PRIMARY KEY (FacultyID, CourseID),
        FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID),
        FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
    );

    CREATE TABLE Enrollment (
        EnrollmentID INT AUTO_INCREMENT PRIMARY KEY,
        StudentID INT NOT NULL,
        CourseID INT NOT NULL,
        EnrollmentDate DATE NOT NULL,
        Status ENUM('Active','Dropped','Completed') NOT NULL,
        UNIQUE (StudentID, CourseID),
        FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
        FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
    );
    
    CREATE TABLE Prerequisite ( 
        CourseID INT NOT NULL, 
        PrerequisiteCourseID INT NOT NULL, 
        PRIMARY KEY (CourseID, PrerequisiteCourseID), 
        FOREIGN KEY (CourseID) REFERENCES Course(CourseID), 
        FOREIGN KEY (PrerequisiteCourseID) REFERENCES Course(CourseID) 
    ); 

    -- 4. FINANCE & REQUESTS
    CREATE TABLE Payment ( 
        PaymentID INT AUTO_INCREMENT PRIMARY KEY, 
        StudentID INT NOT NULL, 
        Amount DECIMAL(10,2) NOT NULL, 
        PaymentDate DATETIME NOT NULL, 
        PaymentType ENUM('Tuition','Fine','Hostel','Other') NOT NULL, 
        Status ENUM('Paid','Pending') NOT NULL, 
        FOREIGN KEY (StudentID) REFERENCES Student(StudentID) 
    ); 
    
    CREATE TABLE PaymentAudit ( 
        AuditID INT AUTO_INCREMENT PRIMARY KEY, 
        PaymentID INT NOT NULL, 
        AdminID INT NOT NULL, 
        Action ENUM('Verified','Flagged','Adjusted','Refunded','Commented') NOT NULL, 
        Notes TEXT, 
        OccurredAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
        FOREIGN KEY (PaymentID) REFERENCES Payment(PaymentID) ON DELETE CASCADE, 
        FOREIGN KEY (AdminID) REFERENCES Admin(AdminID) 
    ); 

    CREATE TABLE Request ( 
        RequestID INT AUTO_INCREMENT PRIMARY KEY, 
        StudentID INT NOT NULL, 
        RequestType ENUM('InfoUpdate','Certificate','IDReissue') NOT NULL, 
        RequestDate DATETIME NOT NULL, 
        Status ENUM('Pending','Approved','Rejected') NOT NULL, 
        ApprovedBy INT, 
        ApprovedAt DATETIME, 
        FOREIGN KEY (StudentID) REFERENCES Student(StudentID), 
        FOREIGN KEY (ApprovedBy) REFERENCES Admin(AdminID) 
    );

    -- 5. ANNOUNCEMENTS
    CREATE TABLE Announcement ( 
        AnnouncementID INT AUTO_INCREMENT PRIMARY KEY, 
        PostedBy INT NOT NULL, 
        Message TEXT NOT NULL, 
        DatePosted DATETIME NOT NULL, 
        FOREIGN KEY (PostedBy) REFERENCES Person(PersonID) 
    );

    -- DATA POPULATION
    INSERT INTO Department (DeptCode, DeptName) VALUES ('CS', 'Computer Science');
    INSERT INTO Program (ProgramCode, ProgramName, DepartmentID) VALUES ('BTECH-CS', 'B.Tech in Computer Science', 1);

    INSERT INTO Person (Name, DOB, Gender, Email, Phone, Address, Password, Role) VALUES 
    ('Alice Administrator', '1985-05-10', 'F', 'admin@uni.edu', '1234567890', 'Admin Block A', 'admin123', 'Admin'),
    ('Dr. Bob Smith', '1978-08-22', 'M', 'bob@uni.edu', '9876543210', 'Faculty Housing B', 'bobpass', 'Faculty'),
    ('Dave Student', '2004-01-15', 'M', 'dave@uni.edu', '1112223333', 'Hostel Block C', 'davepass', 'Student');

    INSERT INTO Admin (AdminID, RoleType) VALUES (1, 'SuperAdmin');
    INSERT INTO Faculty (FacultyID, Designation, DepartmentID, Qualification) VALUES (2, 'Professor', 1, 'PhD in AI');
    INSERT INTO Student (StudentID, RollNo, ProgramID, Semester, AdmissionYear) VALUES (3, 'CS-2023-001', 1, 3, 2023);

    INSERT INTO Request (StudentID, RequestType, RequestDate, Status) VALUES (3, 'Certificate', NOW(), 'Pending');
    INSERT INTO Announcement (PostedBy, Message, DatePosted) VALUES (1, 'Welcome to the new portal!', NOW());
    """

    with app.app_context():
        uri = app.config['SQLALCHEMY_DATABASE_URI']
        root_uri = uri.rsplit('/', 1)[0]
        db_name = uri.rsplit('/', 1)[1].split('?')[0]
        
        engine = db.create_engine(root_uri)
        with engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            conn.execute(text(f"USE {db_name}"))
            
            # Execute statements safely
            for statement in sql_script.split(';'):
                if statement.strip():
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        print(f"❌ Error executing statement:\n{statement[:50]}...\nError: {e}")
                        return # Stop if error
            conn.commit()
        print("✅ Database loaded successfully. 'Request' table created.")

if __name__ == '__main__':
    setup()