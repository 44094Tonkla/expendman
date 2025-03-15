from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

app = Flask(__name__)

cred = credentials.Certificate("D:\Tonkla\cred file\cred_file.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://final-project-expense-tracker-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# เปลี่ยนจาก users เป็น transactions
ref = db.reference('transactions')
# เพิ่ม reference สำหรับ summary
summary_ref = db.reference('summary')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')

# API สำหรับดึงข้อมูลทั้งหมด
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        transactions = ref.get()
        return jsonify(transactions if transactions else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API สำหรับเพิ่มข้อมูล
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        new_transaction = {
            'date': data['date'],
            'category': data['category'],
            'income': float(data['income']),
            'expense': float(data['expense']),
            'note': data['note'],
            'timestamp': datetime.now().isoformat()
        }
        
        new_ref = ref.push(new_transaction)
        return jsonify({'id': new_ref.key}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API สำหรับลบข้อมูล
@app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        ref.child(transaction_id).delete()
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API สำหรับรีเซ็ตข้อมูลทั้งหมด
@app.route('/api/transactions/reset', methods=['POST'])
def reset_transactions():
    try:
        ref.delete()
        return jsonify({'message': 'All transactions reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary', methods=['POST'])
def save_summary_api():
    try:
        data = request.json
        print("Received summary data:", data)  # Debug: แสดงข้อมูลที่ได้รับ
        
        # แปลงข้อมูลเป็นตัวเลขเพื่อให้แน่ใจว่าจะถูกบันทึกอย่างถูกต้อง
        summary_data = {
            'income_total': float(data['income_total']),
            'expense_total': float(data['expense_total']),
            'total_balance': float(data['total_balance']),
            'updated_at': data['updated_at']
        }
        
        # บันทึกข้อมูลลง Firebase
        summary_ref.set(summary_data)
        
        # ตรวจสอบว่าข้อมูลถูกบันทึกจริงหรือไม่
        saved_data = summary_ref.get()
        print("Data saved to Firebase:", saved_data)
        
        return jsonify({'message': 'Summary saved successfully'}), 200
    except Exception as e:
        print("Error saving summary:", str(e))  # Debug: แสดงข้อผิดพลาด
        return jsonify({'error': str(e)}), 500

# API สำหรับดึงข้อมูล summary
@app.route('/api/summary', methods=['GET'])
def get_summary():
    try:
        summary_data = summary_ref.get()
        return jsonify(summary_data if summary_data else {
            'income_total' : 0,
            'expense_total': 0,
            'total_balance': 0,
            'updated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
