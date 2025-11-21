const API_BASE = '/api';

let refreshInterval = null;

function showToast(message, type = 'info') {
  const $toast = $('#toast');
  $toast.text(message);
  $toast.attr('class', `show ${type}`);
  setTimeout(() => {
    $toast.removeClass('show');
  }, 3000);
}

function loadRooms() {
  $.ajax({
    url: `${API_BASE}/monitor/roomstatus`,
    method: 'GET',
    success: function(rooms) {
      const $tbody = $('#rooms-body');
      $tbody.empty();
      
      $.each(rooms, function(index, room) {
        const statusClass = room.roomStatus === 'OCCUPIED' ? 'status-occupied' : 
                           room.roomStatus === 'MAINTENANCE' ? 'status-maintenance' : 'status-available';
        const queueClass = room.queueState === 'SERVING' ? 'queue-serving' : 
                          room.queueState === 'WAITING' ? 'queue-waiting' : '';
        
        // 操作按钮（维修相关）
        let actionButtons = '';
        if (room.roomStatus === 'AVAILABLE') {
          actionButtons = `<button class="btn btn-danger btn-sm" onclick="takeRoomOffline(${room.roomId})">标记维修</button>`;
        } else if (room.roomStatus === 'MAINTENANCE') {
          actionButtons = `<button class="btn btn-primary btn-sm" onclick="bringRoomOnline(${room.roomId})">恢复可用</button>`;
        } else if (room.roomStatus === 'OCCUPIED') {
          actionButtons = '<span style="color: #999;" title="已入住房间不能标记为维修，请先办理退房">--</span>';
        } else {
          actionButtons = '<span style="color: #999;">--</span>';
        }
        
        // 空调控制按钮（已入住或空闲房间都可以操作）
        let acControls = '';
        if (room.roomStatus === 'OCCUPIED' || room.roomStatus === 'AVAILABLE') {
          if (room.acOn) {
            acControls = `
              <div class="ac-controls">
                <button class="btn btn-danger btn-sm" onclick="powerOff(${room.roomId})" title="关机">关机</button>
                <button class="btn btn-primary btn-sm" onclick="changeTemp(${room.roomId})" title="改温度">改温度</button>
                <button class="btn btn-primary btn-sm" onclick="changeSpeed(${room.roomId})" title="改风速">改风速</button>
              </div>
            `;
          } else {
            acControls = `
              <div class="ac-controls">
                <button class="btn btn-primary btn-sm" onclick="powerOn(${room.roomId})" title="开机">开机</button>
              </div>
            `;
          }
        } else {
          acControls = '<span style="color: #999;">--</span>';
        }
        
        const $tr = $('<tr>').html(`
          <td>${room.roomId}</td>
          <td><span class="status-badge ${statusClass}">${getStatusText(room.roomStatus)}</span></td>
          <td>${room.currentTemp?.toFixed(1) || '--'}°C</td>
          <td>${room.targetTemp || '--'}°C</td>
          <td>${getFanSpeedText(room.fanSpeed)}</td>
          <td>${room.acOn ? '开启' : '关闭'}</td>
          <td class="${queueClass}">${getQueueStateText(room.queueState || 'IDLE')}</td>
          <td>${actionButtons}</td>
          <td>${acControls}</td>
        `);
        $tbody.append($tr);
      });
    },
    error: function() {
      showToast('加载房间状态失败', 'error');
    }
  });
}

function loadQueues() {
  $.ajax({
    url: `${API_BASE}/ac/schedule/status`,
    method: 'GET',
    success: function(data) {
      const $servingList = $('#serving-list');
      const $waitingList = $('#waiting-list');
      const $servingCount = $('#serving-count');
      const $waitingCount = $('#waiting-count');
      const $capacityInfo = $('#queue-capacity-info');
      
      $servingList.empty();
      $waitingList.empty();
      
      const capacity = data.capacity || 0;
      const timeSlice = data.timeSlice || 120;
      const servingCountNum = data.servingQueue?.length || 0;
      const waitingCountNum = data.waitingQueue?.length || 0;
      
      $capacityInfo.text(`容量：${servingCountNum}/${capacity}`);
      $servingCount.text(`(${servingCountNum})`);
      $waitingCount.text(`(${waitingCountNum})`);
      
      // 更新调度策略说明中的动态数值
      $('#strategy-capacity, #strategy-capacity-2').text(capacity);
      $('#strategy-time-slice').text(timeSlice);
      
      if (data.servingQueue && data.servingQueue.length > 0) {
        $.each(data.servingQueue, function(index, item) {
          const $li = $('<li>').html(`
            <span>房间 ${item.roomId}</span>
            <span style="margin: 0 10px;">风速：${getFanSpeedText(item.fanSpeed)}</span>
            <span style="color: #666; font-size: 0.85rem;">目标温度：${item.targetTemp || '--'}°C</span>
          `);
          $servingList.append($li);
        });
      } else {
        const $li = $('<li>').text('暂无房间').css('color', '#999');
        $servingList.append($li);
      }
      
      if (data.waitingQueue && data.waitingQueue.length > 0) {
        $.each(data.waitingQueue, function(index, item) {
          const $li = $('<li>').html(`
            <span>房间 ${item.roomId}</span>
            <span style="margin: 0 10px;">风速：${getFanSpeedText(item.fanSpeed)}</span>
            <span style="color: #666; font-size: 0.85rem;">等待中...</span>
          `);
          $waitingList.append($li);
        });
      } else {
        const $li = $('<li>').text('暂无房间').css('color', '#999');
        $waitingList.append($li);
      }
    },
    error: function() {
      showToast('加载队列状态失败', 'error');
    }
  });
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

function getFanSpeedText(speed) {
  const map = {
    'LOW': '低风',
    'MEDIUM': '中风',
    'HIGH': '高风'
  };
  return map[speed] || speed || '--';
}

function getNextFanSpeed(currentSpeed) {
  const speeds = ['LOW', 'MEDIUM', 'HIGH'];
  const currentIndex = speeds.indexOf(currentSpeed || 'LOW');
  const nextIndex = (currentIndex + 1) % speeds.length;
  return speeds[nextIndex];
}

function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    loadRooms();
    loadQueues();
  }, 5000);
}

$(document).ready(function() {
  $('#btn-refresh-rooms').on('click', loadRooms);
  $('#btn-refresh-queues').on('click', loadQueues);
  
  $('[data-action]').on('click', function() {
    const roomId = parseInt($('#maintenance-room-id').val());
    if (!roomId) {
      showToast('请输入房间号', 'error');
      return;
    }
    const action = $(this).data('action');
    const endpoint = action === 'offline' ? 'offline' : 'online';
    
    $.ajax({
      url: `${API_BASE}/admin/rooms/${roomId}/${endpoint}`,
      method: 'POST',
      success: function(data) {
        showToast(data.message || '操作成功', 'success');
        loadRooms();
      },
      error: function(xhr) {
        const data = xhr.responseJSON || {};
        showToast(data.error || '操作失败', 'error');
      }
    });
  });
  
  $('#btn-force-rotation').on('click', function() {
    $.ajax({
      url: `${API_BASE}/admin/maintenance/force-rotation`,
      method: 'POST',
      success: function(data) {
        const $resultDiv = $('#admin-result');
        $resultDiv.addClass('show');
        $resultDiv.html(`<pre>${JSON.stringify(data, null, 2)}</pre>`);
        showToast('强制轮转完成', 'success');
        loadQueues();
      },
      error: function() {
        showToast('强制轮转失败', 'error');
      }
    });
  });
  
  $('#btn-simulate-temp').on('click', function() {
    $.ajax({
      url: `${API_BASE}/admin/maintenance/simulate-temperature`,
      method: 'POST',
      success: function(data) {
        const $resultDiv = $('#admin-result');
        $resultDiv.addClass('show');
        $resultDiv.html(`<pre>${JSON.stringify(data, null, 2)}</pre>`);
        showToast('温度模拟完成', 'success');
        loadRooms();
      },
      error: function() {
        showToast('温度模拟失败', 'error');
      }
    });
  });
  
  loadRooms();
  loadQueues();
  startAutoRefresh();
});

window.takeRoomOffline = function(roomId) {
  $.ajax({
    url: `${API_BASE}/admin/rooms/${roomId}/offline`,
    method: 'POST',
    success: function(data) {
      showToast(data.message || '房间已标记为维修', 'success');
      loadRooms();
    },
    error: function(xhr) {
      const data = xhr.responseJSON || {};
      showToast(data.error || '操作失败', 'error');
    }
  });
};

window.bringRoomOnline = function(roomId) {
  $.ajax({
    url: `${API_BASE}/admin/rooms/${roomId}/online`,
    method: 'POST',
    success: function(data) {
      showToast(data.message || '房间已恢复可用', 'success');
      loadRooms();
    },
    error: function(xhr) {
      const data = xhr.responseJSON || {};
      showToast(data.error || '操作失败', 'error');
    }
  });
};

window.powerOn = function(roomId) {
  $.ajax({
    url: `${API_BASE}/ac/room/${roomId}/status`,
    method: 'GET',
    success: function(statusData) {
      const currentTemp = statusData.currentTemp || 32;
      $.ajax({
        url: `${API_BASE}/ac/room/${roomId}/start?currentTemp=${currentTemp}`,
        method: 'POST',
        success: function(data) {
          showToast(data.message || '空调已开启', 'success');
          loadRooms();
          loadQueues();
        },
        error: function(xhr) {
          const data = xhr.responseJSON || {};
          showToast(data.error || '开机失败', 'error');
        }
      });
    },
    error: function() {
      const currentTemp = 32;
      $.ajax({
        url: `${API_BASE}/ac/room/${roomId}/start?currentTemp=${currentTemp}`,
        method: 'POST',
        success: function(data) {
          showToast(data.message || '空调已开启', 'success');
          loadRooms();
          loadQueues();
        },
        error: function(xhr) {
          const data = xhr.responseJSON || {};
          showToast(data.error || '开机失败', 'error');
        }
      });
    }
  });
};

window.powerOff = function(roomId) {
  $.ajax({
    url: `${API_BASE}/ac/room/${roomId}/stop`,
    method: 'POST',
    success: function(data) {
      showToast(data.message || '空调已关闭', 'success');
      loadRooms();
      loadQueues();
    },
    error: function(xhr) {
      const data = xhr.responseJSON || {};
      showToast(data.error || '关机失败', 'error');
    }
  });
};

window.changeTemp = function(roomId) {
  const currentTemp = prompt('请输入新的目标温度（18-30°C）：');
  if (currentTemp === null) {
    return;
  }
  
  const temp = parseFloat(currentTemp);
  if (isNaN(temp) || temp < 18 || temp > 30) {
    showToast('请输入18-30之间的有效温度值', 'error');
    return;
  }
  
  $.ajax({
    url: `${API_BASE}/ac/room/${roomId}/temp?targetTemp=${temp}`,
    method: 'PUT',
    success: function(data) {
      showToast(data.message || '温度已设置', 'success');
      loadRooms();
    },
    error: function(xhr) {
      const data = xhr.responseJSON || {};
      showToast(data.error || '设置失败', 'error');
    }
  });
};

window.changeSpeed = function(roomId) {
  $.ajax({
    url: `${API_BASE}/ac/room/${roomId}/status`,
    method: 'GET',
    success: function(statusData) {
      const currentSpeed = statusData.fanSpeed || 'LOW';
      const nextSpeed = getNextFanSpeed(currentSpeed);
      
      $.ajax({
        url: `${API_BASE}/ac/room/${roomId}/speed?fanSpeed=${nextSpeed}`,
        method: 'PUT',
        success: function(data) {
          showToast(data.message || `风速已切换为${getFanSpeedText(nextSpeed)}`, 'success');
          loadRooms();
          loadQueues();
        },
        error: function(xhr) {
          const data = xhr.responseJSON || {};
          showToast(data.error || '设置失败', 'error');
        }
      });
    },
    error: function() {
      showToast('获取当前风速失败', 'error');
    }
  });
};
