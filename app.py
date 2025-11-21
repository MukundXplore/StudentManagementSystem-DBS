from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = 'sau_secret_key_2025'  # Change for production

# Database Configuration
# IMPORTANT: Update this connection string with your actual MySQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/sau'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
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

class Student(db.Model):
    __tablename__ = 'Student'
    StudentID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    RollNo = db.Column(db.String(30), unique=True)
    ProgramID = db.Column(db.Integer)
    Semester = db.Column(db.Integer)
    AdmissionYear = db.Column(db.Integer)
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/invalid-login')
def invalid_login():
    return render_template('invalid-login.html')

# --- ADMIN SECTION ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form.get('adminId')
        password = request.form.get('password')
        admin_user = Admin.query.filter_by(AdminID=admin_id).first()
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

@app.route('/admin/users')
def admin_users():
    if session.get('role') != 'Admin': return redirect(url_for('admin_login'))
    return render_template('admin/users.html')

@app.route('/admin/courses')
def admin_courses():
    if session.get('role') != 'Admin': return redirect(url_for('admin_login'))
    return render_template('admin/courses.html')

@app.route('/admin/approvals')
def admin_approvals():
    if session.get('role') != 'Admin': return redirect(url_for('admin_login'))
    return render_template('admin/approvals.html')

@app.route('/admin/announcements')
def admin_announcements():
    if session.get('role') != 'Admin': return redirect(url_for('admin_login'))
    return render_template('admin/announcements.html')

# --- FACULTY SECTION ---
@app.route('/faculty', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        faculty_id = request.form.get('facultyId')
        password = request.form.get('password')
        fac_user = Faculty.query.filter_by(FacultyID=faculty_id).first()
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

@app.route('/faculty/courses')
def faculty_courses():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/courses.html')

@app.route('/faculty/students')
def faculty_students():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/students.html')

@app.route('/faculty/assignments')
def faculty_assignments():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/assignments.html')

@app.route('/faculty/submissions')
def faculty_submissions():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/submissions.html')

@app.route('/faculty/attendance')
def faculty_attendance():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/attendance.html')

@app.route('/faculty/exams')
def faculty_exams():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/exams.html')

@app.route('/faculty/feedback')
def faculty_feedback():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/feedback.html')

@app.route('/faculty/announcements')
def faculty_announcements():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/announcements.html')

@app.route('/faculty/documents')
def faculty_documents():
    if session.get('role') != 'Faculty': return redirect(url_for('faculty_login'))
    return render_template('faculty/documents.html')

# --- STUDENT SECTION ---
@app.route('/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        identifier = request.form.get('enrollmentId')
        password_input = request.form.get('password') # CHANGED: Using password instead of DOB
        
        student = Student.query.filter((Student.StudentID == identifier) | (Student.RollNo == identifier)).first()
        
        if student and student.person.Password == password_input:
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

@app.route('/student/courses')
def student_courses():
    if session.get('role') != 'Student': return redirect(url_for('student_login'))
    return render_template('student/courses.html')

@app.route('/student/assignments')
def student_assignments():
    if session.get('role') != 'Student': return redirect(url_for('student_login'))
    return render_template('student/assignments.html')

@app.route('/student/grades')
def student_grades():
    if session.get('role') != 'Student': return redirect(url_for('student_login'))
    return render_template('student/grades.html')

@app.route('/student/attendance')
def student_attendance():
    if session.get('role') != 'Student': return redirect(url_for('student_login'))
    return render_template('student/attendance.html')

@app.route('/student/timetable')
def student_timetable():
    if session.get('role') != 'Student': return redirect(url_for('student_login'))
    return render_template('student/timetable.html')

@app.route('/student/fees')
def student_fees():
    if session.get('role') != 'Student': return redirect(url_for('student_login'))
    return render_template('student/fees.html')

# --- ACTION ROUTES (Dummies for POST forms) ---
@app.route('/post_announcement', methods=['POST'])
def post_announcement():
    # Add logic to save announcement to DB here
    flash("Announcement Posted!")
    return redirect(url_for('faculty_announcements'))

@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    # Add logic to update attendance here
    flash("Attendance Updated!")
    return redirect(url_for('faculty_attendance'))

@app.route('/update_marks', methods=['POST'])
def update_marks():
    # Add logic to update marks here
    flash("Marks Updated!")
    return redirect(url_for('faculty_exams'))

@app.route('/upload_document', methods=['POST'])
def upload_document():
    # Add logic to save document link here
    flash("Document Link Uploaded!")
    return redirect(url_for('faculty_documents'))

if __name__ == '__main__':
    app.run(debug=True)