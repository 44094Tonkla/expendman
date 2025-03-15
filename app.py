from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os
import json

app = Flask(__name__)

try:
    print("Initializing Firebase...")
    # ลองใช้ client_email และ private_key โดยตรงแทนที่จะใช้ไฟล์ credentials
    # ใช้ได้ทั้งในเครื่องและบน Render
    
    # ลองใช้ environment variable ก่อน
    if os.environ.get('FIREBASE_CLIENT_EMAIL') and os.environ.get('FIREBASE_PRIVATE_KEY'):
        print("Using environment variables for Firebase credentials")
        firebase_creds = {
            "type": "service_account",
            "project_id": "final-project-expense-tracker",
            "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
            "private_key": os.environ.get('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
            "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.environ.get('FIREBASE_CLIENT_ID', ''),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL', '')
        }
        cred = credentials.Certificate(firebase_creds)
    else:
        # ถ้าไม่มี environment variable ให้ใช้ไฟล์
        print("Using credentials file")
        cred_path = "cred_file.json"
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Credential file not found at {os.path.abspath(cred_path)}")
        cred = credentials.Certificate(cred_path)
    
    # initialize Firebase app
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://final-project-expense-tracker-default-rtdb.asia-southeast1.firebasedatabase.app'
    })
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Error initializing Firebase: {str(e)}")
    # อย่าขัดจังหวะการรันแอพ แต่ให้แสดงข้อผิดพลาด
    print("Application will continue but Firebase operations will fail")

# กำหนด Reference
try:
    ref = db.reference('transactions')
    summary_ref = db.reference('summary')
except Exception as e:
    print(f"Error setting up database references: {str(e)}")
    # กำหนดค่าเริ่มต้นเพื่อไม่ให้โปรแกรมหยุดทำงาน
    ref = None
    summary_ref = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')

# API: ดึงข้อมูล transactions ทั้งหมด
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        if ref is None:
            return jsonify({'error': 'Firebase not initialized correctly'}), 500
        transactions = ref.get()
        return jsonify(transactions if transactions else {})
    except Exception as e:
        print(f"Error getting transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: เพิ่ม transaction ใหม่
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        if ref is None:
            return jsonify({'error': 'Firebase not initialized correctly'}), 500
        data = request.json
        new_transaction = {
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'category': data.get('category', 'Uncategorized'),
            'income': float(data.get('income', 0)),
            'expense': float(data.get('expense', 0)),
            'note': data.get('note', ''),
            'timestamp': datetime.now().isoformat()
        }
        new_ref = ref.push(new_transaction)
        return jsonify({'id': new_ref.key}), 201
    except Exception as e:
        print(f"Error adding transaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: ลบ transaction
@app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        if ref is None:
            return jsonify({'error': 'Firebase not initialized correctly'}), 500
        ref.child(transaction_id).delete()
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        print(f"Error deleting transaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: รีเซ็ต transactions ทั้งหมด
@app.route('/api/transactions/reset', methods=['POST'])
def reset_transactions():
    try:
        if ref is None:
            return jsonify({'error': 'Firebase not initialized correctly'}), 500
        ref.delete()
        return jsonify({'message': 'All transactions reset successfully'}), 200
    except Exception as e:
        print(f"Error resetting transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: บันทึก summary
@app.route('/api/summary', methods=['POST'])
def save_summary_api():
    try:
        if summary_ref is None:
            return jsonify({'error': 'Firebase not initialized correctly'}), 500
        data = request.json
        summary_data = {
            'income_total': float(data.get('income_total', 0)),
            'expense_total': float(data.get('expense_total', 0)),
            'total_balance': float(data.get('total_balance', 0)),
            'updated_at': data.get('updated_at', datetime.now().isoformat())
        }
        summary_ref.set(summary_data)
        return jsonify({'message': 'Summary saved successfully'}), 200
    except Exception as e:
        print(f"Error saving summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: ดึงข้อมูล summary
@app.route('/api/summary', methods=['GET'])
def get_summary():
    try:
        if summary_ref is None:
            return jsonify({'error': 'Firebase not initialized correctly'}), 500
        summary_data = summary_ref.get()
        return jsonify(summary_data if summary_data else {
            'income_total': 0,
            'expense_total': 0,
            'total_balance': 0,
            'updated_at': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error getting summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
