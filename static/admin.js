const API_BASE = '/api';

let refreshInterval = null;

async function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `show ${type}`;
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

async function loadRooms() {
  try {
    const res = await fetch(`${API_BASE}/monitor/roomstatus`);
    const rooms = await res.json();
    const tbody = document.getElementById('rooms-body');
    tbody.innerHTML = '';
    
    rooms.forEach(room => {
      const tr = document.createElement('tr');
      const statusClass = room.roomStatus === 'OCCUPIED' ? 'status-occupied' : 
                         room.roomStatus === 'MAINTENANCE' ? 'status-maintenance' : 'status-available';
      const queueClass = room.queueState === 'SERVING' ? 'queue-serving' : 
                        room.queueState === 'WAITING' ? 'queue-waiting' : '';
      tr.innerHTML = `
        <td>${room.roomId}</td>
        <td><span class="status-badge ${statusClass}">${getStatusText(room.roomStatus)}</span></td>
        <td>${room.currentTemp?.toFixed(1) || '--'}°C</td>
        <td>${room.targetTemp || '--'}°C</td>
        <td>${room.fanSpeed || '--'}</td>
        <td>${room.acOn ? '开启' : '关闭'}</td>
        <td class="${queueClass}">${getQueueStateText(room.queueState)}</td>
        <td>
          ${room.roomStatus === 'AVAILABLE' ? 
            `<button class="btn btn-danger btn-sm" onclick="takeRoomOffline(${room.roomId})">标记维修</button>` : 
            room.roomStatus === 'MAINTENANCE' ? 
            `<button class="btn btn-primary btn-sm" onclick="bringRoomOnline(${room.roomId})">恢复可用</button>` : 
            '<span style="color: #999;">--</span>'}
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (error) {
    showToast('加载房间状态失败', 'error');
  }
}

async function loadQueues() {
  try {
    const res = await fetch(`${API_BASE}/monitor/queuestatus`);
    const data = await res.json();
    
    const servingList = document.getElementById('serving-list');
    const waitingList = document.getElementById('waiting-list');
    servingList.innerHTML = '';
    waitingList.innerHTML = '';
    
    data.servingQueue.forEach(item => {
      const li = document.createElement('li');
      li.textContent = `房间 ${item.roomId} · 风速 ${item.fanSpeed}`;
      servingList.appendChild(li);
    });
    
    data.waitingQueue.forEach(item => {
      const li = document.createElement('li');
      li.textContent = `房间 ${item.roomId} · 风速 ${item.fanSpeed}`;
      waitingList.appendChild(li);
    });
  } catch (error) {
    showToast('加载队列状态失败', 'error');
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

function getQueueStateText(state) {
  const map = {
    'SERVING': '服务中',
    'WAITING': '等待中',
    'IDLE': '空闲'
  };
  return map[state] || state;
}

function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    loadRooms();
    loadQueues();
  }, 5000);
}

document.getElementById('btn-refresh-rooms').addEventListener('click', loadRooms);
document.getElementById('btn-refresh-queues').addEventListener('click', loadQueues);

document.querySelectorAll('[data-action]').forEach(btn => {
  btn.addEventListener('click', async () => {
    const roomId = parseInt(document.getElementById('maintenance-room-id').value);
    if (!roomId) {
      showToast('请输入房间号', 'error');
      return;
    }
    const action = btn.dataset.action;
    try {
      const endpoint = action === 'offline' ? 'offline' : 'online';
      const res = await fetch(`${API_BASE}/admin/rooms/${roomId}/${endpoint}`, {
        method: 'POST'
      });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message || '操作成功', 'success');
        loadRooms();
      } else {
        showToast(data.error || '操作失败', 'error');
      }
    } catch (error) {
      showToast('操作失败', 'error');
    }
  });
});

document.getElementById('btn-force-rotation').addEventListener('click', async () => {
  try {
    const res = await fetch(`${API_BASE}/admin/maintenance/force-rotation`, {
      method: 'POST'
    });
    const data = await res.json();
    const resultDiv = document.getElementById('admin-result');
    resultDiv.className = 'result show';
    resultDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    showToast('强制轮转完成', 'success');
    loadQueues();
  } catch (error) {
    showToast('强制轮转失败', 'error');
  }
});

document.getElementById('btn-simulate-temp').addEventListener('click', async () => {
  try {
    const res = await fetch(`${API_BASE}/admin/maintenance/simulate-temperature`, {
      method: 'POST'
    });
    const data = await res.json();
    const resultDiv = document.getElementById('admin-result');
    resultDiv.className = 'result show';
    resultDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    showToast('温度模拟完成', 'success');
    loadRooms();
  } catch (error) {
    showToast('温度模拟失败', 'error');
  }
});

window.takeRoomOffline = async function(roomId) {
  try {
    const res = await fetch(`${API_BASE}/admin/rooms/${roomId}/offline`, {
      method: 'POST'
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || '房间已标记为维修', 'success');
      loadRooms();
    } else {
      showToast(data.error || '操作失败', 'error');
    }
  } catch (error) {
    showToast('操作失败', 'error');
  }
};

window.bringRoomOnline = async function(roomId) {
  try {
    const res = await fetch(`${API_BASE}/admin/rooms/${roomId}/online`, {
      method: 'POST'
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || '房间已恢复可用', 'success');
      loadRooms();
    } else {
      showToast(data.error || '操作失败', 'error');
    }
  } catch (error) {
    showToast('操作失败', 'error');
  }
};

loadRooms();
loadQueues();
startAutoRefresh();

