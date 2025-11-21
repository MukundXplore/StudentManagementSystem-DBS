from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = 'sau_secret_key_2025'  # Change for production

# Database Configuration
# UPDATE the connection string below with your actual MySQL credentials
# Format: mysql+pymysql://username:password@host/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/sau'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS (Mapped to your New Schema)
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
    Password = db.Column(db.String(255))  # Plain text as per your schema
    Role = db.Column(db.Enum('Student', 'Faculty', 'Admin'))

class Student(db.Model):
    __tablename__ = 'Student'
    StudentID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    RollNo = db.Column(db.String(30), unique=True)
    ProgramID = db.Column(db.Integer)
    Semester = db.Column(db.Integer)
    AdmissionYear = db.Column(db.Integer)
    
    # Relationship to fetch Name/DOB/Password from Person table
    person = db.relationship('Person', backref='student_profile')

class Faculty(db.Model):
    __tablename__ = 'Faculty'
    FacultyID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    Designation = db.Column(db.String(60))
    DepartmentID = db.Column(db.Integer)
    Qualification = db.Column(db.String(120))
    
    person = db.relationship('Person', backref='faculty_profile')

class Admin(db.Model):
    __tablename__ = 'Admin'
    AdminID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    RoleType = db.Column(db.Enum('SuperAdmin', 'DeptAdmin', 'FinanceAdmin'))
    
    person = db.relationship('Person', backref='admin_profile')

# ==========================================
# ROUTES & AUTHENTICATION
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')

# --- ADMIN LOGIN ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form.get('adminId')
        password = request.form.get('password')
        
        # 1. Find Admin by AdminID
        admin_user = Admin.query.filter_by(AdminID=admin_id).first()
        
        # 2. If found, check Password in parent Person table
        if admin_user and admin_user.person.Password == password:
            session['user_id'] = admin_user.AdminID
            session['role'] = 'Admin'
            session['name'] = admin_user.person.Name
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('invalid-login.html')

    return render_template('admin/index.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'Admin': return redirect(url_for('admin_login'))
    return render_template('admin/dashboard.html', user_name=session.get('name'))


# --- FACULTY LOGIN ---
@app.route('/faculty', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        faculty_id = request.form.get('facultyId')
        password = request.form.get('password')
        
        # 1. Find Faculty by FacultyID
        fac_user = Faculty.query.filter_by(FacultyID=faculty_id).first()
        
        # 2. Check Password
        if fac_user and fac_user.person.Password == password:
            session['user_id'] = fac_user.FacultyID
            session['role'] = 'Faculty'
            session['name'] = fac_user.person.Name
            return redirect(url_for('faculty_dashboard'))
        else:
            return render_template('invalid-login.html')

    return render_template('faculty/index.html')

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/dashboard.html', user_name=session.get('name'))


# --- STUDENT LOGIN (ID/RollNo + DOB) ---
@app.route('/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        identifier = request.form.get('enrollmentId') # Can be StudentID (e.g., 4) or RollNo (e.g., CS 2023-001)
        dob_input = request.form.get('dob') # Format YYYY-MM-DD
        
        # 1. Try to find student by ID OR RollNo
        student = Student.query.filter((Student.StudentID == identifier) | (Student.RollNo == identifier)).first()
        
        if student:
            # 2. Validate DOB (Convert input string to date object)
            input_date = datetime.datetime.strptime(dob_input, '%Y-%m-%d').date()
            
            if student.person.DOB == input_date:
                session['user_id'] = student.StudentID
                session['role'] = 'Student'
                session['name'] = student.person.Name
                return redirect(url_for('student_dashboard'))
        
        return render_template('invalid-login.html')

    return render_template('student/index.html')

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'Student': return redirect(url_for('student_login'))
    return render_template('student/dashboard.html', user_name=session.get('name'))


# --- LOGOUT & UTILS ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/invalid-login')
def invalid_login():
    return render_template('invalid-login.html')

if __name__ == '__main__':
    app.run(debug=True)