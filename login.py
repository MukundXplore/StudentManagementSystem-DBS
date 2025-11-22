from flask import Blueprint, render_template, request, redirect, url_for, session
from models import Student, Faculty, Admin  # Import models from our new shared file

# Create a Blueprint named 'auth'
login_bp = Blueprint('auth', __name__)

# ==========================================
# PUBLIC & LOGIN ROUTES
# ==========================================

@login_bp.route('/')
def home():
    return render_template('index.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.home')) # Note: 'auth.home' refers to the home function in this blueprint

@login_bp.route('/invalid-login')
def invalid_login():
    return render_template('invalid-login.html')

# --- Student Login ---
@login_bp.route('/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        identifier = request.form.get('enrollmentId')
        password = request.form.get('password')
        
        student = Student.query.filter((Student.StudentID == identifier) | (Student.RollNo == identifier)).first()
        
        if student and student.person.Password == password:
            session['user_id'] = student.StudentID
            session['role'] = 'Student'
            session['name'] = student.person.Name
            return redirect(url_for('student_dashboard')) # Redirects to main app route
        
        return render_template('invalid-login.html')
    return render_template('student/index.html')

# --- Faculty Login ---
@login_bp.route('/faculty', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        faculty_id = request.form.get('facultyId')
        password = request.form.get('password')
        fac = Faculty.query.filter_by(FacultyID=faculty_id).first()
        if fac and fac.person.Password == password:
            session['user_id'] = fac.FacultyID
            session['role'] = 'Faculty'
            session['name'] = fac.person.Name
            return redirect(url_for('faculty_dashboard')) # Redirects to main app route
        return render_template('invalid-login.html')
    return render_template('faculty/index.html')

# --- Admin Login ---
@login_bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form.get('adminId')
        password = request.form.get('password')
        adm = Admin.query.filter_by(AdminID=admin_id).first()
        if adm and adm.person.Password == password:
            session['user_id'] = adm.AdminID
            session['role'] = 'Admin'
            session['name'] = adm.person.Name
            return redirect(url_for('admin_dashboard.dashboard')) # Note: points to admin blueprint
        return render_template('invalid-login.html')
    return render_template('admin/index.html')