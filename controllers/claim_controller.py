from flask import render_template, request, redirect, url_for, session
from models.claim import Claim
from models.low_income_claim import LowIncomeClaim
from models.high_income_claim import HighIncomeClaim
import sqlite3
import random
import datetime

def get_db():
    conn = sqlite3.connect('gov_system.db')
    conn.row_factory = sqlite3.Row 
    return conn

# ==========================================
# ส่วนของประชาชน 
# ==========================================
def index():
    if 'user_id' not in session or session.get('role') != 'citizen':
        return redirect(url_for('login', next=request.url))
    
    conn = get_db()
    claimant_id = session.get('claimant_id')
    
    # 1. ดึงข้อมูลส่วนตัว
    claimant = conn.execute("SELECT * FROM Claimants WHERE id = ?", (claimant_id,)).fetchone()
    
    # 2. ดึงประวัติคำขอทั้งหมด
    history = conn.execute('''
        SELECT c.*, cm.amount, cm.calc_date 
        FROM Claims c 
        LEFT JOIN Compensations cm ON c.claim_id = cm.claim_id
        WHERE c.claimant_id = ? 
        ORDER BY c.request_date DESC, c.claim_id DESC
    ''', (claimant_id,)).fetchall()
    

    latest_claim = history[0] if history else None
    
    conn.close()
    
    return render_template('claims/citizen_home.html', 
                           claimant=claimant, 
                           history=history, 
                           latest_claim=latest_claim)

def create():
    if 'user_id' not in session or session.get('role') != 'citizen':
        return redirect(url_for('login', next=request.url))

    conn = get_db()
    claimant_id = session.get('claimant_id')
    
    # เช็คก่อนว่ามีคำขอที่ "รอตรวจสอบ" 
    pending_claim = conn.execute("SELECT * FROM Claims WHERE claimant_id = ? AND status = 'Pending'", (claimant_id,)).fetchone()
    
    if pending_claim:
        conn.close()
        return redirect(url_for('claim_index'))

    claimant = conn.execute("SELECT * FROM Claimants WHERE id = ?", (claimant_id,)).fetchone()

    if request.method == 'POST':

        salary = claimant['salary']
        if salary < 6500: model = LowIncomeClaim(salary)
        elif salary > 50000: model = HighIncomeClaim(salary)
        else: model = Claim(salary)
            
        amount = model.calculate_compensation()
        claim_id = str(random.randint(10000000, 99999999))
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Claims (claim_id, claimant_id, request_date, status) VALUES (?, ?, ?, ?)",
                       (claim_id, claimant_id, datetime.date.today(), 'Pending'))
        cursor.execute("INSERT INTO Compensations (claim_id, amount, calc_date) VALUES (?, ?, ?)",
                       (claim_id, amount, datetime.date.today()))
        conn.commit()
        conn.close()
        return redirect(url_for('claim_index'))

    conn.close()
    return render_template('claims/citizen_create.html', claimant=claimant)


# === ส่วน Admin ===
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', next=request.url))

    conn = get_db()
    claims = conn.execute('''
        SELECT c.claim_id, cl.first_name, cl.last_name, cl.salary, c.status, cm.amount, 
               c.request_date, cm.calc_date
        FROM Claimants cl
        LEFT JOIN Claims c ON cl.id = c.claimant_id
        LEFT JOIN Compensations cm ON c.claim_id = cm.claim_id
        ORDER BY CASE WHEN c.status = 'Pending' THEN 1 ELSE 2 END, c.request_date DESC
    ''').fetchall()
    
    stats = {
        'total_citizens': conn.execute("SELECT COUNT(*) FROM Claimants").fetchone()[0],
        'approved': conn.execute("SELECT COUNT(*) FROM Claims WHERE status='Approved'").fetchone()[0],
        'pending': conn.execute("SELECT COUNT(*) FROM Claims WHERE status='Pending'").fetchone()[0],
        'budget': conn.execute("SELECT SUM(amount) FROM Compensations JOIN Claims ON Compensations.claim_id = Claims.claim_id WHERE Claims.status='Approved'").fetchone()[0] or 0
    }
    conn.close()
    return render_template('claims/admin_dashboard.html', claims=claims, stats=stats)
# อัปเดตสถานะเป็น Approved
def approve_claim(claim_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Claims SET status = 'Approved' WHERE claim_id = ?", (claim_id,))
    cursor.execute("UPDATE Compensations SET calc_date = ? WHERE claim_id = ?", (datetime.date.today(), claim_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))