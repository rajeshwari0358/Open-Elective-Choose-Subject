import re
import secrets
from flask import render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app import app, get_db, login_manager
from models import Admin, Student
from pdf_generator import generate_student_list_pdf
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from datetime import datetime


db = get_db()

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('admin_'):
        oid = user_id.split('_')[1]
        user_data = db.admins.find_one({'_id': ObjectId(oid)})
        if user_data:
            return Admin(user_data)
    elif user_id.startswith('student_'):
        oid = user_id.split('_')[1]
        user_data = db.students.find_one({'_id': ObjectId(oid)})
        if user_data:
            return Student(user_data)
    return None

@app.route('/')
def index():
    return render_template('index.html')

def is_admin():
    return current_user.is_authenticated and hasattr(current_user, 'user_type') and current_user.user_type == 'admin'

def is_student():
    return current_user.is_authenticated and hasattr(current_user, 'user_type') and current_user.user_type == 'student'

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin():
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin_data = db.admins.find_one({'username': username.strip().lower() if username else None})
        
        if admin_data and Admin.check_password(admin_data['password_hash'], password):
            login_user(Admin(admin_data))
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('student_login'))
    
    branches = list(db.branches.find())
    
    branch_data = []
    total_students = 0
    total_subjects = 0
    
    for branch in branches:
        subjects = list(db.subjects.find({'branch_code': branch['code']}))
        total_subjects += len(subjects)
        
        # Get students in this branch who have enrolled
        students_in_branch = list(db.students.find({'branch_code': branch['code']}))
        enrolled_students_list = []
        
        for student_doc in students_in_branch:
            enrollment = db.enrollments.find_one({
                'student_id': student_doc['_id'],
                'confirmed': True
            })
            
            if enrollment:
                subject = db.subjects.find_one({'_id': enrollment['subject_id']})
                if subject:
                    enrolled_students_list.append({
                        'name': student_doc['name'],
                        'usn': student_doc['usn'],
                        'branch': branch['code'],
                        'subject_code': subject['code'],
                        'subject_name': subject['name']
                    })
        
        total_students += len(enrolled_students_list)
        
        branch_data.append({
            'branch': branch,
            'subjects': subjects,
            'students': enrolled_students_list
        })
    
    return render_template('admin/dashboard.html', 
                         branch_data=branch_data,
                         total_students=total_students,
                         total_subjects=total_subjects)

@app.route('/admin/add-branch', methods=['POST'])
@login_required
def add_branch():
    if not is_admin():
        return redirect(url_for('student_login'))
    
    branch_code = request.form.get('branch_code', '').strip().upper()
    branch_name = request.form.get('branch_name', '').strip()
    
    if not branch_code or len(branch_code) < 2:
        flash('Branch code must be at least 2 characters', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not re.match(r'^[A-Z0-9]+$', branch_code):
        flash('Branch code must contain only letters and digits', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not branch_name:
        flash('Branch name is required', 'error')
        return redirect(url_for('admin_dashboard'))
    
    existing = db.branches.find_one({'code': branch_code})
    if existing:
        flash('Branch code already exists', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.branches.insert_one({'code': branch_code, 'name': branch_name})
    
    flash(f'Branch {branch_code} added successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-subject', methods=['POST'])
@login_required
def add_subject():
    if not is_admin():
        return redirect(url_for('student_login'))
    
    subject_code = request.form.get('subject_code', '').strip().upper()
    subject_name = request.form.get('subject_name', '').strip()
    branch_id_str = request.form.get('branch_id') # This is actually ObjectId in string or branch_code?
    # In template we passed data.branch.id. In Mongo it is ObjectId.
    
    if len(subject_code) < 7:
        flash('Subject code must be at least 7 characters', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not re.match(r'^[A-Z0-9]+$', subject_code):
        flash('Subject code must contain only letters and digits', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not subject_name:
        flash('Subject name is required', 'error')
        return redirect(url_for('admin_dashboard'))
    
    existing = db.subjects.find_one({'code': subject_code})
    if existing:
        flash('Subject code already exists', 'error')
        return redirect(url_for('admin_dashboard'))
    
    branch = db.branches.find_one({'_id': ObjectId(branch_id_str)})
    if not branch:
        flash('Invalid branch', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.subjects.insert_one({
        'code': subject_code,
        'name': subject_name,
        'branch_code': branch['code']
    })
    
    flash(f'Subject {subject_code} added successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-subject/<subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not is_admin():
        return redirect(url_for('student_login'))
    
    subject = db.subjects.find_one({'_id': ObjectId(subject_id)})
    if not subject:
        flash('Subject not found', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.enrollments.delete_many({'subject_id': ObjectId(subject_id)})
    db.subjects.delete_one({'_id': ObjectId(subject_id)})
    
    flash(f'Subject {subject["code"]} deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/download-pdf/<branch_code>')
@login_required
def download_pdf(branch_code):
    if not is_admin():
        return redirect(url_for('student_login'))
    
    branch = db.branches.find_one({'code': branch_code})
    if not branch:
        flash('Branch not found', 'error')
        return redirect(url_for('admin_dashboard'))
    
    students_in_branch = list(db.students.find({'branch_code': branch_code}))
    students = []
    
    for student in students_in_branch:
        enrollment = db.enrollments.find_one({
            'student_id': student['_id'],
            'confirmed': True
        })
        if enrollment:
            subject = db.subjects.find_one({'_id': enrollment['subject_id']})
            students.append({
                'sl_no': len(students) + 1,
                'name': student['name'],
                'usn': student['usn'],
                'branch': branch['code'],
                'subject_code': subject['code'] if subject else 'Unknown',
                'subject_name': subject['name'] if subject else 'Unknown'
            })
    
    pdf_buffer = generate_student_list_pdf(branch['name'], students, branch_code)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=open_elective_{branch_code}_students.pdf'
    
    return response

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if is_student():
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        usn = request.form.get('usn', '').strip().upper()
        password = request.form.get('password')
        
        student_data = db.students.find_one({'usn': usn})
        
        if student_data and Student.check_password(student_data['password_hash'], password):
            login_user(Student(student_data))
            return redirect(url_for('student_dashboard'))
        flash('Invalid USN or password', 'error')
    
    return render_template('student/login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    branches = list(db.branches.find())
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        usn = request.form.get('usn', '').strip().upper()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        branch_id = request.form.get('branch_id')
        
        if not all([name, usn, password, confirm_password, branch_id]):
            flash('All fields are required', 'error')
            return render_template('student/register.html', branches=branches)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('student/register.html', branches=branches)
        
        if db.students.find_one({'usn': usn}):
            flash('USN already registered', 'error')
            return render_template('student/register.html', branches=branches)
        
        # Get branch code
        branch = db.branches.find_one({'_id': ObjectId(branch_id)})
        if not branch:
             flash('Invalid branch', 'error')
             return render_template('student/register.html', branches=branches)

        password_hash = generate_password_hash(password)
        db.students.insert_one({
            'name': name,
            'usn': usn,
            'branch_code': branch['code'],
            'password_hash': password_hash,
            'created_at': datetime.utcnow()
        })
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('student_login'))
    
    return render_template('student/register.html', branches=branches)

@app.route('/student/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        usn = request.form.get('usn', '').strip().upper()
        name = request.form.get('name', '').strip()
        
        student = db.students.find_one({'usn': usn})
        
        if student and student['name'].lower() == name.lower():
            new_password = secrets.token_urlsafe(8)
            password_hash = generate_password_hash(new_password)
            
            db.students.update_one(
                {'_id': student['_id']},
                {'$set': {'password_hash': password_hash}}
            )
            
            flash(f'Your new password is: {new_password}. Please save it and login.', 'success')
            return redirect(url_for('student_login'))
        
        flash('No student found with this USN and name combination', 'error')
    
    return render_template('student/forgot_password.html')

@app.route('/student/logout')
@login_required
def student_logout():
    logout_user()
    return redirect(url_for('student_login'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if not is_student():
        return redirect(url_for('admin_login'))
    
    # Get all branches with their subjects
    branches = list(db.branches.find())
    
    # Attach subjects to each branch object for the template
    # NOTE: The template expects 'branch.subjects' which is a list
    # Since we are passing dictionaries (from Mongo), we can just add the key
    for branch in branches:
        branch['subjects'] = list(db.subjects.find({'branch_code': branch['code']}))

    enrollment = db.enrollments.find_one({'student_id': ObjectId(current_user.id)})
    
    # If enrollment exists, fetch subject details to display
    if enrollment:
        subject = db.subjects.find_one({'_id': enrollment['subject_id']})
        if subject:
             enrollment['subject'] = subject
             # Also need branch for the subject
             subject_branch = db.branches.find_one({'code': subject['branch_code']})
             enrollment['subject']['branch'] = subject_branch

    # Need to pass current_user object that has 'branch' attribute for template: {{ current_user.branch.code }}
    # Our Student model has branch_code. We might need to augment it or the template.
    # The models.py Student class has self.branch_code. 
    # But template accesses {{ current_user.branch.code }} which implies an object.
    # We should update models.py Student to have a property 'branch' that returns an object with code and name
    # OR update the template.
    # Let's update the Student object in this route context or in UserLoader, 
    # but UserLoader is cached/simple. 
    # Easiest is to make a simple wrapper for branch in the Student class or just fetch it here.
    # Actually, let's fix the Student class in models.py to have a branch property.
    # Wait, I can't easily change models.py from here.
    # I will modify Student class in models.py later or just monkey patch it here?
    # Better: Update models.py content in the write step. I already wrote models.py.
    # I will re-write models.py to be smarter.

    return render_template('student/dashboard.html', 
                         branches=branches,
                         enrollment=enrollment)

@app.route('/student/select-subject/<subject_id>', methods=['POST'])
@login_required
def select_subject(subject_id):
    if not is_student():
        return redirect(url_for('admin_login'))
    
    subject = db.subjects.find_one({'_id': ObjectId(subject_id)})
    if not subject:
         flash('Subject not found', 'error')
         return redirect(url_for('student_dashboard'))
    
    if subject['branch_code'] == current_user.branch_code:
        flash('You cannot select subjects from your own branch', 'error')
        return redirect(url_for('student_dashboard'))
    
    existing = db.enrollments.find_one({'student_id': ObjectId(current_user.id)})
    
    if existing:
        if existing.get('confirmed'):
            flash('You have already confirmed your subject selection', 'error')
            return redirect(url_for('student_dashboard'))
        
        db.enrollments.update_one(
            {'_id': existing['_id']},
            {'$set': {
                'subject_id': ObjectId(subject_id),
                'enrolled_at': datetime.utcnow()
            }}
        )
    else:
        db.enrollments.insert_one({
            'student_id': ObjectId(current_user.id),
            'subject_id': ObjectId(subject_id),
            'enrolled_at': datetime.utcnow(),
            'confirmed': False
        })
    
    return redirect(url_for('confirm_subject'))

@app.route('/student/confirm-subject', methods=['GET', 'POST'])
@login_required
def confirm_subject():
    if not is_student():
        return redirect(url_for('admin_login'))
    
    enrollment = db.enrollments.find_one({'student_id': ObjectId(current_user.id)})
    
    if not enrollment:
        flash('Please select a subject first', 'error')
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        db.enrollments.update_one(
            {'_id': enrollment['_id']},
            {'$set': {'confirmed': True}}
        )
        flash('Subject selection confirmed successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    
    # Fetch details for display
    subject = db.subjects.find_one({'_id': enrollment['subject_id']})
    enrollment['subject'] = subject
    
    return render_template('student/confirm_subject.html', enrollment=enrollment)

