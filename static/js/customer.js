// 尝试从 URL 参数获取 roomId (例如: /customer?roomId=1)
const urlParams = new URLSearchParams(window.location.search);
let currentRoomId = urlParams.get('roomId');

// 如果 URL 里没有，尝试从 localStorage 获取（记住上次的）
if (!currentRoomId) {
    currentRoomId = localStorage.getItem('lastRoomId');
}

// 如果还是没有，提示用户输入
if (!currentRoomId) {
    currentRoomId = prompt("请输入当前房间号:", "1");
}

// 转换为数字类型
if (currentRoomId) {
    currentRoomId = parseInt(currentRoomId);
    if (isNaN(currentRoomId)) {
        currentRoomId = null;
    }
}

// 保存到 localStorage，下次不用输入
if (currentRoomId) {
    localStorage.setItem('lastRoomId', currentRoomId.toString());
    // 更新页面上的显示
    const roomDisplay = document.getElementById('room-id-display');
    if (roomDisplay) {
        roomDisplay.textContent = currentRoomId;
    }
}

let refreshInterval = null;
let isUserEditing = false;
let isUserEditingSpeed = false;

function showToast(message, type = 'info') {
  // 使用原生 JavaScript 实现，不依赖 jQuery
  // 如果页面有 toast 元素，则显示；否则使用 console.log
  const toastEl = document.getElementById('toast');
  if (toastEl) {
    toastEl.textContent = message;
    toastEl.className = `show ${type}`;
    setTimeout(() => {
      toastEl.classList.remove('show');
    }, 3000);
  } else {
    // 如果没有 toast 元素，使用 console 输出（开发时有用）
    console.log(`[${type.toUpperCase()}] ${message}`);
  }
}

function loadRooms() {
  // 注意：这个函数可能不再需要，因为 customer.js 已经改为使用 /ac/state
  // 保留此函数以兼容旧代码，但实际可能不会被调用
  $.ajax({
    url: `${API_BASE}/hotel/rooms`,
    method: 'GET',
    success: function(rooms) {
      const $selector = $('#room-selector');
      $selector.html('<option value="">请选择房间</option>');
      
      const occupiedRooms = rooms.filter(room => (room.roomStatus || room.status) === 'OCCUPIED');
      if (occupiedRooms.length === 0) {
        $selector.append($('<option>').prop('disabled', true).text('暂无已入住房间'));
        return;
      }
      
      $.each(occupiedRooms, function(index, room) {
        const $option = $('<option>')
          .val(room.roomId || room.id)
          .text(`房间 ${room.roomId || room.id} - 已入住`);
        $selector.append($option);
      });
    },
    error: function() {
      showToast('加载房间列表失败', 'error');
    }
  });
}

// === 核心：获取状态并渲染 ===
function updateState() {
    if (!currentRoomId) return;

    // !!! 注意这里：必须是 /ac/state，不能是 /api/ac/state !!!
    axios.get(`/ac/state?roomId=${currentRoomId}`)  
        .then(response => {
            renderUI(response.data);
        })
        .catch(error => {
            console.error(error);
            // 如果出错，打印请求的 URL 看看是不是还在发旧的
            console.log("请求失败，当前请求地址:", `/ac/state?roomId=${currentRoomId}`);
            document.getElementById('ac-status').innerText = "连接断开";
        });
}

function renderUI(data) {
    // 更新温度显示
    const currentTempEl = document.getElementById('current-temp');
    if (currentTempEl) {
        currentTempEl.textContent = data.current_temp ? data.current_temp.toFixed(1) : '--';
    }
    
    // 更新目标温度
    const targetTempEl = document.getElementById('target-temp');
    if (targetTempEl) {
        targetTempEl.textContent = data.target_temp || '25';
    }
    
    // 更新风速
    const fanSpeedEl = document.getElementById('fan-speed');
    if (fanSpeedEl) {
        fanSpeedEl.textContent = data.fan_speed || '--';
    }
    
    // 更新空调状态
    const acStatusEl = document.getElementById('ac-status');
    if (acStatusEl) {
        acStatusEl.textContent = data.ac_on ? '开启' : '关闭';
    }
    
    // 更新模式
    const modeEl = document.getElementById('mode');
    if (modeEl) {
        modeEl.textContent = data.ac_mode || '--';
    }
    
    // 更新费用
    const costEl = document.getElementById('cost');
    if (costEl) {
        costEl.textContent = (data.current_cost || 0).toFixed(2);
    }
    
    const totalFeeEl = document.getElementById('total-fee');
    if (totalFeeEl) {
        totalFeeEl.textContent = (data.total_cost || 0).toFixed(2);
    }
}

// 保留 loadRoomStatus 作为别名，以兼容旧代码
function loadRoomStatus(roomId) {
    if (roomId) {
        currentRoomId = roomId;
    }
    updateState();
}

function loadUsageStats(roomId) {
    // 费用信息已经在 updateState 中通过 renderUI 更新了
    // 这个方法保留为空，以兼容旧代码
}

function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    if (currentRoomId) {
      updateState();
    }
  }, 3000);
}

// === 3. 控制指令 (去掉 /api) ===

function powerOn() {
    if (!currentRoomId) return;
    // !!! 去掉 /api !!!
    axios.post('/ac/power', { roomId: currentRoomId })
        .then(() => updateState())
        .catch(err => alert("开机失败: " + (err.response?.data?.error || err.message)));
}

function powerOff() {
    if (!currentRoomId) return;
    // !!! 去掉 /api !!!
    axios.post('/ac/power/off', { roomId: currentRoomId })
        .then(() => updateState())
        .catch(err => alert("关机失败: " + (err.response?.data?.error || err.message)));
}

function changeTemp(delta) {
    if (!currentRoomId) return;
    
    const targetTempEl = document.getElementById('target-temp');
    if (!targetTempEl) return;
    
    const currentTemp = parseFloat(targetTempEl.textContent) || 25;
    const newTemp = Math.max(18, Math.min(30, currentTemp + delta));
    
    // !!! 去掉 /api !!!
    axios.post('/ac/temp', { 
        roomId: currentRoomId, 
        targetTemp: newTemp 
    })
    .then(() => {
        targetTempEl.textContent = newTemp;
        updateState();
    })
    .catch(err => alert("调温失败: " + (err.response?.data?.error || err.message)));
}

function changeSpeed(speed) {
    if (!currentRoomId) return;
    // !!! 去掉 /api !!!
    axios.post('/ac/speed', { 
        roomId: currentRoomId, 
        fanSpeed: speed 
    })
    .then(() => updateState())
    .catch(err => alert("调速失败: " + (err.response?.data?.error || err.message)));
}

function changeMode(mode) {
    if (!currentRoomId) return;
    // !!! 去掉 /api !!!
    axios.post('/ac/mode', { 
        roomId: currentRoomId, 
        mode: mode 
    })
    .then(() => updateState())
    .catch(err => alert("切换模式失败: " + (err.response?.data?.error || err.message)));
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 如果已经通过 URL 参数或 localStorage 获取到房间号，自动启动
    if (currentRoomId) {
        updateState();
        startAutoRefresh();
    } else {
        // 如果没有房间号，显示提示
        const acStatusEl = document.getElementById('ac-status');
        if (acStatusEl) {
            acStatusEl.textContent = "请通过 URL 参数指定房间号，例如: /customer?roomId=1";
        }
    }
});
