async function displayData() {
    try {
        const response = await fetch('/api/transactions');
        const data = await response.json();
        
        const tableBody = document.getElementById('data-table');
        const totalIncomeElement = document.getElementById('totalIncome');
        const totalExpenseElement = document.getElementById('totalExpense');
        const finalBalanceElement = document.getElementById('finalBalance');

        if (!data || Object.keys(data).length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">ไม่มีข้อมูล</td></tr>';
            totalIncomeElement.textContent = '0.00';
            totalExpenseElement.textContent = '0.00';
            finalBalanceElement.textContent = '0.00';
            return;
        }

        let totalIncome = 0;
        let totalExpense = 0;
        tableBody.innerHTML = '';

        // แปลงข้อมูลเป็น array และเรียงตามวันที่
        const sortedData = Object.entries(data)
            .map(([id, item]) => ({ id, ...item }))
            .sort((a, b) => new Date(b.date) - new Date(a.date));

        sortedData.forEach(item => {
            const income = parseFloat(item.income) || 0;
            const expense = parseFloat(item.expense) || 0;
            const balance = income - expense;
            totalIncome += income;
            totalExpense += expense;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDate(item.date)}</td>
                <td>${formatCategory(item.category)}</td>
                <td>${income.toLocaleString('th-TH', { minimumFractionDigits: 2 })}</td>
                <td>${expense.toLocaleString('th-TH', { minimumFractionDigits: 2 })}</td>
                <td>${balance.toLocaleString('th-TH', { minimumFractionDigits: 2 })}</td>
                <td>${item.note || '-'}</td>
                <td>
                    <button onclick="deleteEntry('${item.id}')" class="delete-btn">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });

        // อัพเดทสรุปข้อมูล
        totalIncomeElement.textContent = totalIncome.toLocaleString('th-TH', { minimumFractionDigits: 2 });
        totalExpenseElement.textContent = totalExpense.toLocaleString('th-TH', { minimumFractionDigits: 2 });
        finalBalanceElement.textContent = (totalIncome - totalExpense).toLocaleString('th-TH', { minimumFractionDigits: 2 });

        saveSummaryToDatabase(totalIncome, totalExpense, totalIncome - totalExpense);
    } catch (error) {
        console.error('Error:', error);
        alert('เกิดข้อผิดพลาดในการโหลดข้อมูล');
    }
}

async function deleteEntry(id) {
    if (confirm('คุณแน่ใจหรือไม่ที่จะลบรายการนี้?')) {
        try {
            const response = await fetch(`/api/transactions/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                displayData();
            } else {
                const errorData = await response.json();
                alert('เกิดข้อผิดพลาด: ' + (errorData.error || 'ไม่สามารถลบข้อมูลได้'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
        }
    }
}

async function resetData() {
    if (confirm('คุณแน่ใจหรือไม่ที่จะลบข้อมูลทั้งหมด? การกระทำนี้ไม่สามารถย้อนกลับได้')) {
        try {
            const response = await fetch('/api/transactions/reset', {
                method: 'POST'
            });

            if (response.ok) {
                alert('รีเซ็ตข้อมูลสำเร็จ');
                displayData();
            } else {
                const errorData = await response.json();
                alert('เกิดข้อผิดพลาด: ' + (errorData.error || 'ไม่สามารถรีเซ็ตข้อมูลได้'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์');
        }
    }
}

function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    return new Date(dateString).toLocaleDateString('th-TH', options);
}

function formatCategory(category) {
    const categories = {
        'salary': 'เงินเดือน',
        'bonus': 'โบนัส',
        'food': 'อาหาร',
        'transport': 'การเดินทาง',
        'shopping': 'ช้อปปิ้ง',
        'other': 'อื่นๆ'
    };
    return categories[category] || category;
}

function exportToCSV() {
    const rows = document.querySelectorAll('#data-table tr');
    if (rows.length === 0) {
        alert('ไม่มีข้อมูลที่จะส่งออก');
        return;
    }

    let csvContent = "วันที่,หมวดหมู่,รายรับ,รายจ่าย,ยอดคงเหลือ,บันทึก\n";
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length > 0) {
            const rowData = [
                cells[0].textContent,
                cells[1].textContent,
                cells[2].textContent,
                cells[3].textContent,
                cells[4].textContent,
                cells[5].textContent
            ].map(cell => `"${cell}"`).join(',');
            csvContent += rowData + '\n';
        }
    });

    const blob = new Blob(["\ufeff" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `รายรับรายจ่าย_${new Date().toLocaleDateString('th-TH')}.csv`;
    link.click();
}

async function saveSummaryToDatabase(totalIncome, totalExpense, finalBalance) {
    try {
        const summaryData = {
            income_total: totalIncome,
            expense_total: totalExpense,
            total_balance: finalBalance,
            updated_at: new Date().toISOString()
        };

        const response = await fetch('/api/summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(summaryData)
        });

        if (response.ok) {
            console.log('ส่งข้อมูล Summary สำเร็จ ✅');
        } else {
            console.error('เกิดข้อผิดพลาดในการส่งข้อมูล Summary');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// ฟังก์ชั่นสำหรับการค้นหาและกรองข้อมูล
function searchAndFilterData() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    const monthFilter = document.getElementById('monthFilter').value;
    
    const tableRows = document.querySelectorAll('#data-table tr');
    
    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length === 0) return;
        
        const date = cells[0].textContent.toLowerCase();
        const category = cells[1].textContent.toLowerCase();
        const note = cells[5].textContent.toLowerCase();
        
        // กรองตามคำค้นหา
        const matchesSearch = date.includes(searchTerm) || 
                             category.includes(searchTerm) || 
                             note.includes(searchTerm);
        
        // กรองตามหมวดหมู่
        const matchesCategory = categoryFilter === 'all' || 
                                category === formatCategory(categoryFilter).toLowerCase();
        
        // กรองตามเดือน
        let matchesMonth = true;
        if (monthFilter) {
            const rowDate = new Date(date.split(' ')[0]);
            const filterDate = new Date(monthFilter + '-01');
            matchesMonth = rowDate.getMonth() === filterDate.getMonth() && 
                          rowDate.getFullYear() === filterDate.getFullYear();
        }
        
        // แสดงหรือซ่อนแถว
        row.style.display = matchesSearch && matchesCategory && matchesMonth ? '' : 'none';
    });
}

// เรียกใช้งานฟังก์ชันค้นหาเมื่อมีการเปลี่ยนแปลงในฟิลด์ค้นหา
document.addEventListener('DOMContentLoaded', function() {
    displayData();
    document.getElementById('resetButton').addEventListener('click', resetData);
    
    // เพิ่ม event listener สำหรับการค้นหาและกรอง
    document.getElementById('searchInput').addEventListener('input', searchAndFilterData);
    document.getElementById('categoryFilter').addEventListener('change', searchAndFilterData);
    document.getElementById('monthFilter').addEventListener('change', searchAndFilterData);
});