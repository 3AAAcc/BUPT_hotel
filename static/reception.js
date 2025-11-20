const API_BASE = '/api';

async function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `show ${type}`;
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

async function loadAvailableRooms() {
  try {
    const res = await fetch(`${API_BASE}/hotel/rooms/available`);
    const rooms = await res.json();
    const checkinSelect = document.getElementById('checkin-room-id');
    checkinSelect.innerHTML = '<option value="">请选择房间</option>';
    rooms.forEach(room => {
      if (room.status === 'AVAILABLE') {
        const option = document.createElement('option');
        option.value = room.id;
        option.textContent = `房间 ${room.id}`;
        checkinSelect.appendChild(option);
      }
    });
  } catch (error) {
    showToast('加载可用房间失败', 'error');
  }
}

async function loadAllRooms() {
  try {
    const res = await fetch(`${API_BASE}/monitor/roomstatus`);
    const rooms = await res.json();
    const checkoutSelect = document.getElementById('checkout-room-id');
    const tbody = document.getElementById('rooms-body');
    
    checkoutSelect.innerHTML = '<option value="">请选择房间</option>';
    tbody.innerHTML = '';
    
    rooms.forEach(room => {
      const option = document.createElement('option');
      option.value = room.roomId;
      option.textContent = `房间 ${room.roomId}`;
      if (room.roomStatus === 'OCCUPIED') {
        checkoutSelect.appendChild(option);
      }
      
      const tr = document.createElement('tr');
      const statusClass = room.roomStatus === 'OCCUPIED' ? 'status-occupied' : 
                         room.roomStatus === 'MAINTENANCE' ? 'status-maintenance' : 'status-available';
      
      const formatDateTime = (dateStr) => {
        if (!dateStr) return '--';
        try {
          const date = new Date(dateStr);
          return date.toLocaleString('zh-CN', { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit', 
            hour: '2-digit', 
            minute: '2-digit' 
          });
        } catch {
          return dateStr;
        }
      };
      
      tr.innerHTML = `
        <td>${room.roomId}</td>
        <td><span class="status-badge ${statusClass}">${getStatusText(room.roomStatus)}</span></td>
        <td>${room.customerName || '--'}</td>
        <td>${room.customerIdCard || '--'}</td>
        <td>${room.customerPhone || '--'}</td>
        <td>${formatDateTime(room.checkInTime)}</td>
        <td>
          ${room.roomStatus === 'OCCUPIED' ? 
            `<button class="btn btn-danger btn-sm" onclick="checkoutRoom(${room.roomId})">退房</button>` : 
            room.roomStatus === 'AVAILABLE' ? 
            `<button class="btn btn-primary btn-sm" onclick="quickCheckin(${room.roomId})">快速入住</button>` : 
            '--'}
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (error) {
    showToast('加载房间状态失败', 'error');
  }
}

function getStatusText(status) {
  const map = {
    'AVAILABLE': '空闲',
    'OCCUPIED': '已入住',
    'MAINTENANCE': '维修中'
  };
  return map[status] || status;
}

document.getElementById('checkin-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const roomId = parseInt(document.getElementById('checkin-room-id').value);
  const name = document.getElementById('checkin-name').value;
  const idCard = document.getElementById('checkin-id-card').value;
  const phone = document.getElementById('checkin-phone').value;
  
  if (!roomId || !name) {
    showToast('请填写必填项', 'error');
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/hotel/checkin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roomId, name, idCard, phoneNumber: phone })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || '入住成功', 'success');
      document.getElementById('checkin-form').reset();
      loadAvailableRooms();
      loadAllRooms();
    } else {
      showToast(data.error || '入住失败', 'error');
    }
  } catch (error) {
    showToast('办理入住失败', 'error');
  }
});

document.getElementById('checkout-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const roomId = parseInt(document.getElementById('checkout-room-id').value);
  if (!roomId) {
    showToast('请选择房间', 'error');
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/hotel/checkout/${roomId}`, {
      method: 'POST'
    });
    const data = await res.json();
    if (res.ok) {
      const resultDiv = document.getElementById('checkout-result');
      resultDiv.className = 'result show';
      resultDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
      showToast('退房成功', 'success');
      document.getElementById('checkout-form').reset();
      loadAvailableRooms();
      loadAllRooms();
    } else {
      showToast(data.error || '退房失败', 'error');
    }
  } catch (error) {
    showToast('办理退房失败', 'error');
  }
});

document.getElementById('btn-refresh-rooms').addEventListener('click', () => {
  loadAvailableRooms();
  loadAllRooms();
});

window.checkoutRoom = async function(roomId) {
  document.getElementById('checkout-room-id').value = roomId;
  document.getElementById('checkout-form').dispatchEvent(new Event('submit'));
};

window.quickCheckin = function(roomId) {
  document.getElementById('checkin-room-id').value = roomId;
  document.getElementById('checkin-name').focus();
};

loadAvailableRooms();
loadAllRooms();

