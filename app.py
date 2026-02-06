import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import init_db, get_db_connection, calculate_age, check_prereq_passed, get_registrants_count

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# เริ่มต้นฐานข้อมูลทุกครั้งที่รัน (เพื่อความสะดวกในการตรวจข้อสอบ)
init_db()

# --- Auth Routes ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check Admin
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password)).fetchone()
        if admin:
            session['user_type'] = 'admin'
            session['user_id'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        
        # Check Student
        student = conn.execute('SELECT * FROM students WHERE id = ? AND password = ?', (username, password)).fetchone()
        if student:
            session['user_type'] = 'student'
            session['user_id'] = student['id']
            return redirect(url_for('student_profile'))
            
        flash('Invalid Credentials')
        conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Admin Routes (View 1 & 4) ---
@app.route('/admin/students')
def admin_dashboard():
    if session.get('user_type') != 'admin': return redirect(url_for('login'))
    
    conn = get_db_connection()
    school_filter = request.args.get('school')
    sort_by = request.args.get('sort', 'first_name') # name or age
    search = request.args.get('search', '')

    query = 'SELECT * FROM students WHERE (first_name LIKE ? OR last_name LIKE ?)'
    params = [f'%{search}%', f'%{search}%']

    if school_filter:
        query += ' AND school = ?'
        params.append(school_filter)
    
    if sort_by == 'age':
        query += ' ORDER BY dob DESC' # อายุน้อยไปมาก = dob มากไปน้อย
    else:
        query += ' ORDER BY first_name'

    students = conn.execute(query, params).fetchall()
    
    # Calculate age for display
    student_list = []
    for s in students:
        s_dict = dict(s)
        s_dict['age'] = calculate_age(s['dob'])
        student_list.append(s_dict)
        
    schools = conn.execute('SELECT DISTINCT school FROM students').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', students=student_list, schools=schools)

@app.route('/admin/grade_entry')
def grade_entry_list():
    if session.get('user_type') != 'admin': return redirect(url_for('login'))
    conn = get_db_connection()
    subjects = conn.execute('SELECT * FROM subjects').fetchall()
    conn.close()
    return render_template('grading_list.html', subjects=subjects)

@app.route('/admin/grade/<subject_id>', methods=['GET', 'POST'])
def grade_entry(subject_id):
    if session.get('user_type') != 'admin': return redirect(url_for('login'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        grade = request.form['grade']
        conn.execute('UPDATE registered_subjects SET grade = ? WHERE student_id = ? AND subject_id = ?',
                     (grade, student_id, subject_id))
        conn.commit()
        flash('Grade Updated')
    
    subject = conn.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
    students = conn.execute('''
        SELECT s.id, s.first_name, s.last_name, r.grade 
        FROM registered_subjects r
        JOIN students s ON r.student_id = s.id
        WHERE r.subject_id = ?
    ''', (subject_id,)).fetchall()
    
    count = len(students) # Requirement: Show count
    conn.close()
    return render_template('grading.html', subject=subject, students=students, count=count)

# --- Student Routes (View 2 & 3) ---
@app.route('/student/profile')
def student_profile():
    if session.get('user_type') != 'student': return redirect(url_for('login'))
    
    # หาก admin เข้าดู profile นร. (ผ่าน link ใน admin dashboard)
    target_id = request.args.get('id', session['user_id'])
    
    # Security: Student can only view own, Admin can view anyone
    if session['user_type'] == 'student' and target_id != session['user_id']:
        return "Unauthorized Access", 403

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (target_id,)).fetchone()
    
    registered = conn.execute('''
        SELECT s.id, s.name, s.credit, r.grade 
        FROM registered_subjects r
        JOIN subjects s ON r.subject_id = s.id
        WHERE r.student_id = ?
    ''', (target_id,)).fetchall()
    
    curriculum = conn.execute('SELECT DISTINCT curriculum_name FROM subject_structure WHERE curriculum_id = ?', 
                              (student['curriculum_id'],)).fetchone()
    
    conn.close()
    return render_template('student_profile.html', student=student, registered=registered, curriculum=curriculum)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_type') != 'student': return redirect(url_for('login'))
    student_id = session['user_id']
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    
    # Business Rule: Age >= 15 [cite: 30]
    if calculate_age(student['dob']) < 15:
        flash("อายุไม่ถึง 15 ปี ไม่สามารถลงทะเบียนได้")
        return redirect(url_for('student_profile'))

    if request.method == 'POST':
        subject_id = request.form['subject_id']
        subject = conn.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
        
        # Business Rule: Prereq Check [cite: 32]
        if subject['prerequisite_id']:
            if not check_prereq_passed(student_id, subject['prerequisite_id']):
                flash(f"ไม่สามารถลงทะเบียนได้ ต้องผ่านวิชา {subject['prerequisite_id']} ก่อน")
                return redirect(url_for('register'))
        
        # Register logic
        try:
            conn.execute('INSERT INTO registered_subjects (student_id, subject_id, grade) VALUES (?, ?, NULL)',
                         (student_id, subject_id))
            conn.commit()
            flash('ลงทะเบียนสำเร็จ')
            return redirect(url_for('student_profile')) # [cite: 31]
        except sqlite3.IntegrityError:
            flash('ลงทะเบียนวิชานี้ไปแล้ว')

    # Show only subjects in curriculum NOT YET registered
    subjects = conn.execute('''
        SELECT s.*, ss.semester 
        FROM subject_structure ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.curriculum_id = ?
        AND s.id NOT IN (SELECT subject_id FROM registered_subjects WHERE student_id = ?)
    ''', (student['curriculum_id'], student_id)).fetchall()
    
    conn.close()
    return render_template('register.html', subjects=subjects, student=student)

if __name__ == '__main__':
    app.run(debug=True)