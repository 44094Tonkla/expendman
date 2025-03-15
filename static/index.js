async function saveData() {
  const date = document.getElementById('date').value;
  const category = document.getElementById('category').value;
  const income = document.getElementById('income').value;
  const expense = document.getElementById('expense').value;
  const note = document.getElementById('note').value;

  if (!date) {
      alert('กรุณาเลือกวันที่');
      return;
  }

  if (income === '' && expense === '') {
      alert('กรุณากรอกรายรับหรือรายจ่าย');
      return;
  }

  try {
      const response = await fetch('/api/transactions', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              date,
              category,
              income: income || 0,
              expense: expense || 0,
              note
          })
      });

      if (response.ok) {
          alert('บันทึกข้อมูลสำเร็จ!');
          // เคลียร์ฟอร์ม
          document.getElementById('date').value = '';
          document.getElementById('category').value = 'salary';
          document.getElementById('income').value = '';
          document.getElementById('expense').value = '';
          document.getElementById('note').value = '';
          
          // ไปยังหน้าสรุป
          window.location.href = '/summary';
      } else {
          const errorData = await response.json();
          alert('เกิดข้อผิดพลาด: ' + (errorData.error || 'ไม่สามารถบันทึกข้อมูลได้'));
      }
  } catch (error) {
      console.error('Error:', error);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
  }
}

// ตั้งค่าวันที่เริ่มต้นเป็นวันนี้
document.addEventListener('DOMContentLoaded', function() {
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('date').value = today;
});