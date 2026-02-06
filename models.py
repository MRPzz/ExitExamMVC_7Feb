import sqlite3
import datetime

# ต้องกำหนดชื่อ DB ให้ตรงกัน
DB_NAME = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- ส่วนที่หายไป (ที่ Error แจ้ง) ---
def init_db():
    conn = get_db_connection()
    try:
        # ต้องใส่ encoding='utf-8' เพื่อให้อ่านภาษาไทยในไฟล์ schema.sql ได้
        with open('schema.sql', encoding='utf-8') as f:
            conn.executescript(f.read())
    except FileNotFoundError:
        print("Error: ไม่พบไฟล์ schema.sql")
    conn.close()
# --------------------------------

# --- Helper Functions อื่นๆ ---

def calculate_age(dob_str):
    if not dob_str: return 0
    try:
        dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return 0

def check_prereq_passed(student_id, prereq_id):
    if not prereq_id:
        return True
    conn = get_db_connection()
    record = conn.execute('SELECT grade FROM registered_subjects WHERE student_id = ? AND subject_id = ?', 
                          (student_id, prereq_id)).fetchone()
    conn.close()
    if record and record['grade'] and record['grade'] != 'F':
        return True
    return False

def get_registrants_count(subject_id):
    conn = get_db_connection()
    result = conn.execute('SELECT COUNT(*) as c FROM registered_subjects WHERE subject_id = ?', (subject_id,)).fetchone()
    conn.close()
    return result['c'] if result else 0