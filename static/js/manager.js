/**
 * Manager Logic (管理端)
 * 同时负责：
 * 1. 监控调度队列 (/monitor/status)
 * 2. 房间状态与控制 (/admin/rooms/status)
 */

document.addEventListener('DOMContentLoaded', () => {
  refreshAll();
  // 1秒刷新一次，保证极高的实时性
  setInterval(refreshAll, 1000);
});

function refreshAll() {
  loadMonitorData();
  loadRoomData();
}

// === 1. 监控队列部分 ===
function loadMonitorData() {
  axios.get('/monitor/status')
      .then(res => renderMonitor(res.data))
      .catch(err => console.error("监控数据失败:", err));
}

function renderMonitor(data) {
  // 系统指标
  document.getElementById('sys-capacity').innerText = data.capacity;
  document.getElementById('sys-timeslice').innerText = data.timeSlice;

  // 服务队列
  const sList = document.getElementById('serving-list');
  document.getElementById('serving-count').innerText = data.servingQueue.length;
  sList.innerHTML = data.servingQueue.length ? data.servingQueue.map(item => `
      <div class="mini-card serving">
          <div class="mc-top">Room ${item.roomId}</div>
          <div class="mc-btm">
              <span>${item.fanSpeed}</span>
              <span>${item.servingSeconds.toFixed(0)}s</span>
          </div>
      </div>
  `).join('') : '<div style="color:#bdc3c7;font-size:0.8rem;">空闲</div>';

  // 等待队列
  const wList = document.getElementById('waiting-list');
  document.getElementById('waiting-count').innerText = data.waitingQueue.length;
  wList.innerHTML = data.waitingQueue.length ? data.waitingQueue.map(item => `
      <div class="mini-card waiting">
          <div class="mc-top">Room ${item.roomId}</div>
          <div class="mc-btm">
              <span>${item.fanSpeed}</span>
              <span>${item.waitingSeconds.toFixed(0)}s</span>
          </div>
      </div>
  `).join('') : '<div style="color:#bdc3c7;font-size:0.8rem;">无等待</div>';
}

// === 2. 房间控制部分 ===
function loadRoomData() {
  axios.get('/admin/rooms/status')
      .then(res => renderRoomGrid(res.data))
      .catch(err => console.error("房间数据失败:", err));
}

function renderRoomGrid(data) {
  const grid = document.getElementById('admin-room-grid');
  grid.innerHTML = data.map(room => createRoomCard(room)).join('');
}

function createRoomCard(room) {
  // 状态逻辑
  let statusClass = 'status-IDLE';
  let statusText = '关机 (Off)';
  if (room.ac_on) {
      if (room.queueState === 'SERVING') { statusClass = 'status-SERVING'; statusText = '服务中'; }
      else if (room.queueState === 'WAITING') { statusClass = 'status-WAITING'; statusText = '等待中'; }
      else if (room.queueState === 'PAUSED') { statusClass = 'status-WAITING'; statusText = '回温待机'; }
  }

  const totalCost = (room.total_cost || room.totalCost || 0).toFixed(2);
  
  // 增加模式判断
  const isHeat = room.ac_mode === 'HEATING';
  const modeIcon = isHeat ? '<i class="fa-solid fa-fire text-danger"></i>' : '<i class="fa-solid fa-snowflake text-primary"></i>';
  const modeText = isHeat ? '制热' : '制冷';

  // 按钮高亮逻辑
  const getSpeedClass = (s) => (room.fan_speed === s && room.ac_on) ? 'active' : '';
  const getModeClass = (m) => (room.ac_mode === m) ? 'active' : '';

  return `
      <div class="admin-card ${statusClass}">
          <div class="card-status-bar"></div>
          <div class="card-body">
              <div class="card-top">
                  <span class="room-title">Room ${room.room_id}</span>
                  <span class="status-badge">${statusText}</span>
              </div>
              <div class="data-row">
                  <div class="data-item">
                      <span class="label">模式</span>
                      <div class="value" style="font-size: 1.1rem">${modeIcon} ${modeText}</div>
                  </div>
                  <div class="data-item">
                      <span class="label">当前室温</span>
                      <div class="value">${(room.current_temp || 0).toFixed(1)}°</div>
                  </div>
                  <div class="data-item">
                      <span class="label">费用</span>
                      <div class="value cost-val">¥${totalCost}</div>
                  </div>
              </div>
              <div class="control-panel">
                  
                  <div class="ctrl-group" style="grid-column: span 2;">
                      <div class="btn-group-mini">
                          <button class="btn-mini ${getModeClass('COOLING')}" onclick="controlMode(${room.room_id}, 'COOLING')">❄️ 制冷</button>
                          <button class="btn-mini ${getModeClass('HEATING')}" onclick="controlMode(${room.room_id}, 'HEATING')">🔥 制热</button>
                      </div>
                  </div>

                  <div class="ctrl-group">
                      <span class="ctrl-label">目标: ${room.target_temp || 25}°</span>
                      <div class="btn-group-mini">
                          <button class="btn-mini" onclick="controlTemp(${room.room_id}, ${(room.target_temp || 25) - 1})">-</button>
                          <button class="btn-mini" onclick="controlTemp(${room.room_id}, ${(room.target_temp || 25) + 1})">+</button>
                      </div>
                  </div>

                  <div class="ctrl-group">
                      <span class="ctrl-label">风速: ${room.fan_speed || '-'}</span>
                      <div class="btn-group-mini">
                          <button class="btn-mini ${getSpeedClass('LOW')}" onclick="controlSpeed(${room.room_id}, 'LOW')">L</button>
                          <button class="btn-mini ${getSpeedClass('MEDIUM')}" onclick="controlSpeed(${room.room_id}, 'MEDIUM')">M</button>
                          <button class="btn-mini ${getSpeedClass('HIGH')}" onclick="controlSpeed(${room.room_id}, 'HIGH')">H</button>
                      </div>
                  </div>

                  <div style="grid-column: span 2;">
                      ${room.ac_on 
                          ? `<button class="btn-power p-off" onclick="controlPower(${room.room_id}, 'off')">强制关机</button>` 
                          : `<button class="btn-power p-on" onclick="controlPower(${room.room_id}, 'on')">远程开机</button>`
                      }
                  </div>
              </div>
          </div>
      </div>
  `;
}

// === 控制函数 ===
function controlPower(roomId, action) {
  axios.post('/admin/control/power', { roomId, action }).then(refreshAll).catch(err => alert(err));
}
function controlTemp(roomId, targetTemp) {
  axios.post('/admin/control/temp', { roomId, targetTemp }).then(refreshAll).catch(err => alert(err));
}
function controlSpeed(roomId, fanSpeed) {
  axios.post('/admin/control/speed', { roomId, fanSpeed }).then(refreshAll).catch(err => alert(err));
}
function controlMode(roomId, mode) {
  axios.post('/admin/control/mode', { roomId, mode })
      .then(() => {
          // 切换模式后，目标温度可能会变，所以要重新加载数据
          loadRoomData(); 
      })
      .catch(err => alert("切换模式失败: " + err));
}

function resetDatabase() {
  if (!confirm('⚠️ 警告：此操作将清空所有数据并重新初始化数据库！\n\n确定要继续吗？')) {
    return;
  }
  
  if (!confirm('⚠️ 再次确认：这将删除所有房间、客户、账单和详单数据！\n\n确定要重置吗？')) {
    return;
  }
  
  axios.post('/admin/reset-database')
      .then(res => {
          alert('✅ ' + res.data.message);
          // 重置后刷新页面数据
          setTimeout(() => {
              refreshAll();
          }, 500);
      })
      .catch(err => {
          alert('❌ 重置失败: ' + (err.response?.data?.error || err.message));
      });
}