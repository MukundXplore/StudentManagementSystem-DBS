from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Student, Faculty, Admin, Course, Enrollment, Teaches, Announcement, Request, Department, Program
import datetime

# Import our blueprints
from login import login_bp
from admin import admin_bp

app = Flask(__name__)
app.secret_key = 'sau_secret_key_2025'

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mukund23%4015CS@localhost/sau'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# REGISTER BLUEPRINTS
app.register_blueprint(login_bp)
app.register_blueprint(admin_bp)

# ==========================================
# PREVENT CACHING (Fixes "Old Page" issues)
# ==========================================
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ==========================================
# SHARED ACTION ROUTES (Admin & Faculty)
# ==========================================

@app.route('/post_announcement', methods=['POST'])
def post_announcement():
    if 'user_id' not in session:
        return redirect(url_for('auth.home'))

    try:
        title = request.form.get('title')
        body = request.form.get('body')
        # We combine title and body or just use body since DB has 'Message' column
        message = f"{title}: {body}" if title else body
        
        # Create new Announcement
        new_announcement = Announcement(
            PostedBy=session['user_id'],
            Message=message,
            DatePosted=datetime.datetime.now()
        )
        db.session.add(new_announcement)
        db.session.commit()
        flash("Announcement Posted Successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error posting announcement: {str(e)}")

    # Redirect back to the correct dashboard
    if session.get('role') == 'Admin':
        return redirect(url_for('admin_dashboard.announcements'))
    return redirect(url_for('faculty_announcements'))

# ==========================================
# FACULTY ROUTES (Placeholders for now)
# ==========================================

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/dashboard.html', user_name=session.get('name'))

@app.route('/faculty/courses')
def faculty_courses():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    # Use Teaches table to find assigned courses
    courses = db.session.query(Course).join(Teaches).filter(Teaches.FacultyID == session['user_id']).all()
    return render_template('faculty/courses.html', user_name=session.get('name'), courses=courses)

@app.route('/faculty/students')
def faculty_students():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/students.html', user_name=session.get('name'))

@app.route('/faculty/assignments')
def faculty_assignments():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/assignments.html', user_name=session.get('name'))

@app.route('/faculty/submissions')
def faculty_submissions():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/submissions.html', user_name=session.get('name'))

@app.route('/faculty/attendance')
def faculty_attendance():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/attendance.html', user_name=session.get('name'))

@app.route('/faculty/exams')
def faculty_exams():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/exams.html', user_name=session.get('name'))

@app.route('/faculty/feedback')
def faculty_feedback():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/feedback.html', user_name=session.get('name'))

@app.route('/faculty/announcements')
def faculty_announcements():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/announcements.html', user_name=session.get('name'))

@app.route('/faculty/documents')
def faculty_documents():
    if session.get('role') != 'Faculty': return redirect(url_for('auth.faculty_login'))
    return render_template('faculty/documents.html', user_name=session.get('name'))

# ==========================================
# STUDENT ROUTES (Placeholders for now)
# ==========================================

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'Student': return redirect(url_for('auth.student_login'))
    return render_template('student/dashboard.html', user_name=session.get('name'))

@app.route('/student/courses')
def student_courses():
    if session.get('role') != 'Student': return redirect(url_for('auth.student_login'))
    return render_template('student/courses.html', user_name=session.get('name'))

@app.route('/student/assignments')
def student_assignments():
    if session.get('role') != 'Student': return redirect(url_for('auth.student_login'))
    return render_template('student/assignments.html', user_name=session.get('name'))

@app.route('/student/grades')
def student_grades():
    if session.get('role') != 'Student': return redirect(url_for('auth.student_login'))
    return render_template('student/grades.html', user_name=session.get('name'))

@app.route('/student/attendance')
def student_attendance():
    if session.get('role') != 'Student': return redirect(url_for('auth.student_login'))
    return render_template('student/attendance.html', user_name=session.get('name'))

@app.route('/student/timetable')
def student_timetable():
    if session.get('role') != 'Student': return redirect(url_for('auth.student_login'))
    return render_template('student/timetable.html', user_name=session.get('name'))

@app.route('/student/fees')
def student_fees():
    if session.get('role') != 'Student': return redirect(url_for('auth.student_login'))
    return render_template('student/fees.html', user_name=session.get('name'))

# ==========================================
# DUMMY ACTION ROUTES (To prevent crashes)
# ==========================================

@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    flash("Attendance Updated!")
    return redirect(url_for('faculty_attendance'))

@app.route('/update_marks', methods=['POST'])
def update_marks():
    flash("Marks Updated!")
    return redirect(url_for('faculty_exams'))

@app.route('/upload_document', methods=['POST'])
def upload_document():
    flash("Document Link Uploaded!")
    return redirect(url_for('faculty_documents'))

if __name__ == '__main__':
    app.run(debug=True)