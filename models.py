from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ==========================================
# CORE TABLES
# ==========================================
class Person(db.Model):
    __tablename__ = 'Person'
    PersonID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100))
    DOB = db.Column(db.Date)
    Gender = db.Column(db.String(1))
    Email = db.Column(db.String(120), unique=True)
    Phone = db.Column(db.String(20))
    Address = db.Column(db.String(255))
    Password = db.Column(db.String(255))
    Role = db.Column(db.Enum('Student', 'Faculty', 'Admin'))

class Department(db.Model):
    __tablename__ = 'Department'
    DepartmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DeptCode = db.Column(db.String(20), unique=True)
    DeptName = db.Column(db.String(100))

class Program(db.Model):
    __tablename__ = 'Program'
    ProgramID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProgramCode = db.Column(db.String(20), unique=True)
    ProgramName = db.Column(db.String(100))
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Department.DepartmentID'))
    department = db.relationship('Department', backref='programs')

# ==========================================
# ROLES
# ==========================================
class Student(db.Model):
    __tablename__ = 'Student'
    StudentID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    RollNo = db.Column(db.String(30), unique=True)
    ProgramID = db.Column(db.Integer, db.ForeignKey('Program.ProgramID'))
    Semester = db.Column(db.Integer)
    AdmissionYear = db.Column(db.Integer)
    
    person = db.relationship('Person', backref='student_profile')
    program = db.relationship('Program', backref='students')

class Faculty(db.Model):
    __tablename__ = 'Faculty'
    FacultyID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    Designation = db.Column(db.String(60))
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Department.DepartmentID'))
    Qualification = db.Column(db.String(120))
    
    person = db.relationship('Person', backref='faculty_profile')
    department = db.relationship('Department', backref='faculty')

class Admin(db.Model):
    __tablename__ = 'Admin'
    AdminID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    RoleType = db.Column(db.Enum('SuperAdmin', 'DeptAdmin', 'FinanceAdmin'))
    person = db.relationship('Person', backref='admin_profile')

# ==========================================
# ACADEMICS & EXTRAS
# ==========================================
class Course(db.Model):
    __tablename__ = 'Course'
    CourseID = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    CourseName = db.Column(db.String(120))
    Credits = db.Column(db.Integer)
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Department.DepartmentID'))
    Semester = db.Column(db.Integer)
    
    department = db.relationship('Department', backref='courses')

class Teaches(db.Model):
    __tablename__ = 'Teaches'
    FacultyID = db.Column(db.Integer, db.ForeignKey('Faculty.FacultyID'), primary_key=True)
    CourseID = db.Column(db.Integer, db.ForeignKey('Course.CourseID'), primary_key=True)

class Enrollment(db.Model):
    __tablename__ = 'Enrollment'
    EnrollmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StudentID = db.Column(db.Integer, db.ForeignKey('Student.StudentID'))
    CourseID = db.Column(db.Integer, db.ForeignKey('Course.CourseID'))
    Status = db.Column(db.Enum('Active', 'Dropped', 'Completed'))

class Request(db.Model):
    __tablename__ = 'Request'
    RequestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StudentID = db.Column(db.Integer, db.ForeignKey('Student.StudentID'))
    RequestType = db.Column(db.Enum('InfoUpdate','Certificate','IDReissue'))
    RequestDate = db.Column(db.DateTime)
    Status = db.Column(db.Enum('Pending','Approved','Rejected'))
    
    student = db.relationship('Student', backref='requests')

class Announcement(db.Model):
    __tablename__ = 'Announcement'
    AnnouncementID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PostedBy = db.Column(db.Integer, db.ForeignKey('Person.PersonID'))
    Message = db.Column(db.Text)
    DatePosted = db.Column(db.DateTime)
    
    poster = db.relationship('Person', backref='announcements')