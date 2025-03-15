from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os

app = Flask(__name__)

# ตรวจสอบว่า Firebase ถูก initialize หรือยัง
if not firebase_admin._apps:
    cred_path = "cred_file.json"
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Credential file '{cred_path}' not found!")
    
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://final-project-expense-tracker-default-rtdb.asia-southeast1.firebasedatabase.app'
    })

# กำหนด Reference
ref = db.reference('transactions')
summary_ref = db.reference('summary')

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
        transactions = ref.get()
        return jsonify(transactions if transactions else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: เพิ่ม transaction ใหม่
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
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
        return jsonify({'error': str(e)}), 500

# API: ลบ transaction
@app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        ref.child(transaction_id).delete()
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: รีเซ็ต transactions ทั้งหมด
@app.route('/api/transactions/reset', methods=['POST'])
def reset_transactions():
    try:
        ref.delete()
        return jsonify({'message': 'All transactions reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: บันทึก summary
@app.route('/api/summary', methods=['POST'])
def save_summary_api():
    try:
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
        return jsonify({'error': str(e)}), 500

# API: ดึงข้อมูล summary
@app.route('/api/summary', methods=['GET'])
def get_summary():
    try:
        summary_data = summary_ref.get()
        return jsonify(summary_data if summary_data else {
            'income_total': 0,
            'expense_total': 0,
            'total_balance': 0,
            'updated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
