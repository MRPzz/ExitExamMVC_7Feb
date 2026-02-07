from flask import render_template, request, redirect, url_for, session
import sqlite3

def get_db():
    conn = sqlite3.connect('gov_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def login():
    next_url = request.args.get('next')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'citizen':
                session['claimant_id'] = user['claimant_id']

            if next_url:
                return redirect(next_url)
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('claim_index'))
        
        return render_template('auth/login.html', error="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            
    return render_template('auth/login.html')

def logout():
    session.clear()
    return redirect(url_for('login'))