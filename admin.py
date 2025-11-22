from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from sqlalchemy import or_
from models import db, Person, Student, Faculty, Admin, Course, Request, Announcement, Department, Program

admin_bp = Blueprint('admin_dashboard', __name__)

def check_admin_access():
    return session.get('role') == 'Admin'

# ---------------------------------------------------
# 1. DASHBOARD
# ---------------------------------------------------
@admin_bp.route('/admin/dashboard')
def dashboard():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    
    stats = {
        'student_count': Student.query.count(),
        'faculty_count': Faculty.query.count(),
        'course_count': Course.query.count(),
        'pending_requests': Request.query.filter_by(Status='Pending').count()
    }
    return render_template('admin/dashboard.html', user_name=session.get('name'), stats=stats)

# ---------------------------------------------------
# 2. MANAGE USERS (Search + Add + Delete)
# ---------------------------------------------------
@admin_bp.route('/admin/users', methods=['GET', 'POST'])
def users():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))

    # --- HANDLE ADDING NEW USER ---
    if request.method == 'POST':
        try:
            role = request.form.get('role')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password') # Plain text for now (matches your setup)
            
            # 1. Create Person
            new_person = Person(Name=name, Email=email, Password=password, Role=role)
            db.session.add(new_person)
            db.session.flush() # Get PersonID before committing

            # 2. Create Role Entry
            if role == 'Student':
                new_student = Student(
                    StudentID=new_person.PersonID,
                    RollNo=request.form.get('roll_no'),
                    ProgramID=request.form.get('program_id'),
                    Semester=request.form.get('semester'),
                    AdmissionYear=2023
                )
                db.session.add(new_student)
            elif role == 'Faculty':
                new_faculty = Faculty(
                    FacultyID=new_person.PersonID,
                    Designation=request.form.get('designation'),
                    DepartmentID=request.form.get('department_id'),
                    Qualification=request.form.get('qualification')
                )
                db.session.add(new_faculty)
            
            db.session.commit()
            flash(f"{role} added successfully!")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding user: {str(e)}")
        return redirect(url_for('admin_dashboard.users'))

    # --- HANDLE SEARCH & DISPLAY ---
    query = request.args.get('q')
    
    student_q = db.session.query(Student, Person, Program).join(Person).join(Program)
    faculty_q = db.session.query(Faculty, Person, Department).join(Person).join(Department)

    if query:
        search = f"%{query}%"
        student_q = student_q.filter(or_(Person.Name.like(search), Student.RollNo.like(search)))
        faculty_q = faculty_q.filter(or_(Person.Name.like(search), Faculty.Designation.like(search)))

    # Fetch lists for display
    students = student_q.all()
    faculty = faculty_q.all()
    
    # Fetch dropdown options for the Add User Modals
    programs = Program.query.all()
    departments = Department.query.all()

    return render_template('admin/users.html', user_name=session.get('name'), 
                           students=students, faculty=faculty, programs=programs, departments=departments)

@admin_bp.route('/admin/delete_user/<int:user_id>/<string:role>')
def delete_user(user_id, role):
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    
    try:
        # Deleting Person automatically deletes Student/Faculty due to Cascade in SQL
        person = Person.query.get(user_id)
        if person:
            db.session.delete(person)
            db.session.commit()
            flash(f"{role} deleted successfully.")
    except Exception as e:
        flash("Error deleting user.")
    return redirect(url_for('admin_dashboard.users'))

# ---------------------------------------------------
# 3. COURSES (Search + Add + Delete)
# ---------------------------------------------------
@admin_bp.route('/admin/courses', methods=['GET', 'POST'])
def courses():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))

    # --- HANDLE ADD COURSE ---
    if request.method == 'POST':
        try:
            new_course = Course(
                CourseName=request.form.get('course_name'),
                Credits=request.form.get('credits'),
                DepartmentID=request.form.get('department_id'),
                Semester=request.form.get('semester')
            )
            db.session.add(new_course)
            db.session.commit()
            flash("Course added successfully!")
        except:
            flash("Error adding course.")
        return redirect(url_for('admin_dashboard.courses'))

    # --- SEARCH & DISPLAY ---
    query = request.args.get('q')
    course_q = db.session.query(Course, Department).join(Department)
    
    if query:
        search = f"%{query}%"
        course_q = course_q.filter(or_(Course.CourseName.like(search), Department.DeptName.like(search)))
        
    courses = course_q.all()
    departments = Department.query.all() # For the Modal dropdown

    return render_template('admin/courses.html', user_name=session.get('name'), 
                           courses=courses, departments=departments)

@admin_bp.route('/admin/delete_course/<int:course_id>')
def delete_course(course_id):
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    course = Course.query.get(course_id)
    if course:
        db.session.delete(course)
        db.session.commit()
    return redirect(url_for('admin_dashboard.courses'))

# ---------------------------------------------------
# 4. APPROVALS (Approve/Reject)
# ---------------------------------------------------
@admin_bp.route('/admin/approvals')
def approvals():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    
    requests = db.session.query(Request, Student, Person)\
        .join(Student, Request.StudentID == Student.StudentID)\
        .join(Person, Student.StudentID == Person.PersonID)\
        .filter(Request.Status == 'Pending').all()
        
    return render_template('admin/approvals.html', user_name=session.get('name'), requests=requests)

@admin_bp.route('/admin/approve_request/<int:req_id>/<action>')
def process_request(req_id, action):
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    
    req = Request.query.get(req_id)
    if req:
        req.Status = 'Approved' if action == 'approve' else 'Rejected'
        db.session.commit()
        flash(f"Request {req.Status}.")
    return redirect(url_for('admin_dashboard.approvals'))

# ---------------------------------------------------
# 5. ANNOUNCEMENTS
# ---------------------------------------------------
@admin_bp.route('/admin/announcements')
def announcements():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    announcements = Announcement.query.order_by(Announcement.DatePosted.desc()).all()
    return render_template('admin/announcements.html', user_name=session.get('name'), announcements=announcements)