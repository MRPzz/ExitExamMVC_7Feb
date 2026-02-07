import os
from flask import Flask
from controllers import claim_controller, auth_controller
from database.db_setup import init_db 

app = Flask(__name__)
app.secret_key = 'secret_key_for_session_simulation'

# Routes
app.add_url_rule('/', view_func=auth_controller.login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=auth_controller.logout)
app.add_url_rule('/claims', view_func=claim_controller.index, endpoint='claim_index')
app.add_url_rule('/claims/create', view_func=claim_controller.create, methods=['GET', 'POST'], endpoint='claim_create')
app.add_url_rule('/dashboard', view_func=claim_controller.admin_dashboard, endpoint='admin_dashboard')
app.add_url_rule('/claims/approve/<claim_id>', view_func=claim_controller.approve_claim, endpoint='claim_approve')

# Auto setup Database
if not os.path.exists('gov_system.db'):
    print("ไม่พบ Database กำลังเริ่มสร้างตารางใหม่...")
    init_db()
    print("สร้าง Database เรียบร้อยแล้ว")

if __name__ == '__main__':
    app.run(debug=True)