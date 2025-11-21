const API_BASE = '/api';

let currentRoomId = null;
let refreshInterval = null;
let isUserEditing = false;
let isUserEditingSpeed = false;

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

function loadRoomStatus(roomId) {
  $.ajax({
    url: `${API_BASE}/ac/room/${roomId}/status`,
    method: 'GET',
    success: function(data) {
      $('#current-temp').text(`${data.currentTemp?.toFixed(1) || '--'}°C`);
      $('#target-temp').text(`${data.targetTemp || '--'}°C`);
      $('#fan-speed').text(data.fanSpeed || '--');
      $('#ac-status').text(data.acOn ? '开启' : '关闭');
      
      const $tempInput = $('#temp-input');
      if (!isUserEditing && !$tempInput.is(':focus')) {
        $tempInput.val(data.targetTemp || '');
      }
      
      const $speedSelect = $('#speed-select');
      if (!isUserEditingSpeed && !$speedSelect.is(':focus')) {
        $speedSelect.val(data.fanSpeed || 'LOW');
      }
      
      const $acStatusEl = $('#ac-status');
      $acStatusEl.text(data.acOn ? '开启' : '关闭');
      $acStatusEl.css('color', data.acOn ? '#10b981' : '#666');
    },
    error: function() {
      showToast('加载房间状态失败', 'error');
    }
  });
}

function loadUsageStats(roomId) {
  $.ajax({
    url: `${API_BASE}/ac/room/${roomId}/detail`,
    method: 'GET',
    success: function(data) {
      $('#total-duration').text(`${data.totalDuration || 0} 分钟`);
      $('#total-cost').text(`¥${(data.totalCost || 0).toFixed(2)}`);
    },
    error: function() {
      // 不显示错误提示，避免干扰用户
    }
  });
}

function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    if (currentRoomId) {
      loadRoomStatus(currentRoomId);
      loadUsageStats(currentRoomId);
    }
  }, 3000);
}

$(document).ready(function() {
  $('#room-selector').on('change', function() {
    const roomId = parseInt($(this).val());
    if (roomId) {
      currentRoomId = roomId;
      $('#current-room-id').text(roomId);
      $('#room-control').show();
      loadRoomStatus(roomId);
      loadUsageStats(roomId);
      startAutoRefresh();
    } else {
      currentRoomId = null;
      $('#room-control').hide();
      if (refreshInterval) clearInterval(refreshInterval);
    }
  });
  
  $('#btn-refresh-rooms').on('click', loadRooms);
  
  $('#btn-power-on').on('click', function() {
    if (!currentRoomId) return;
    
    $.ajax({
      url: `${API_BASE}/ac/room/${currentRoomId}/status`,
      method: 'GET',
      success: function(statusData) {
        const currentTemp = statusData.currentTemp || 32;
    $.ajax({
      url: `${API_BASE}/ac/room/${currentRoomId}/start?currentTemp=${currentTemp}`,
      method: 'POST',
          success: function(data) {
            showToast(data.message || '空调已开启', 'success');
            loadRoomStatus(currentRoomId);
            loadUsageStats(currentRoomId);
          },
          error: function(xhr) {
            const data = xhr.responseJSON || {};
            showToast(data.error || '开启失败', 'error');
          }
        });
      },
      error: function() {
        const currentTemp = 32;
        $.ajax({
          url: `${API_BASE}/ac/room/${currentRoomId}/start?currentTemp=${currentTemp}`,
          method: 'POST',
          success: function(data) {
            showToast(data.message || '空调已开启', 'success');
            loadRoomStatus(currentRoomId);
            loadUsageStats(currentRoomId);
          },
          error: function(xhr) {
            const data = xhr.responseJSON || {};
            showToast(data.error || '开启失败', 'error');
          }
        });
      }
    });
  });
  
  $('#btn-power-off').on('click', function() {
    if (!currentRoomId) return;
    
    $.ajax({
      url: `${API_BASE}/ac/room/${currentRoomId}/stop`,
      method: 'POST',
      success: function(data) {
        showToast(data.message || '空调已关闭', 'success');
        loadRoomStatus(currentRoomId);
        loadUsageStats(currentRoomId);
      },
      error: function(xhr) {
        const data = xhr.responseJSON || {};
        showToast(data.error || '关闭失败', 'error');
      }
    });
  });
  
  $('#temp-input').on('focus', function() {
    isUserEditing = true;
  }).on('blur', function() {
    isUserEditing = false;
  });
  
  $('#speed-select').on('focus', function() {
    isUserEditingSpeed = true;
  }).on('blur', function() {
    isUserEditingSpeed = false;
  });
  
  $('#btn-set-temp').on('click', function() {
    if (!currentRoomId) {
      showToast('请先选择房间', 'error');
      return;
    }
    
    $.ajax({
      url: `${API_BASE}/ac/room/${currentRoomId}/status`,
      method: 'GET',
      success: function(statusData) {
        if (!statusData.acOn) {
          showToast('请先开启空调', 'error');
          return;
        }
        
        const temp = parseFloat($('#temp-input').val());
        if (!temp || isNaN(temp) || temp < 18 || temp > 30) {
          showToast('请输入18-30之间的有效温度值', 'error');
          return;
        }
        
        $.ajax({
          url: `${API_BASE}/ac/room/${currentRoomId}/temp?targetTemp=${temp}`,
          method: 'PUT',
          success: function(data) {
            showToast(data.message || '温度已设置', 'success');
            isUserEditing = false;
            loadRoomStatus(currentRoomId);
            loadUsageStats(currentRoomId);
          },
          error: function(xhr) {
            const data = xhr.responseJSON || {};
            showToast(data.error || '设置失败', 'error');
          }
        });
      },
      error: function() {
        showToast('检查空调状态失败', 'error');
      }
    });
  });
  
  $('#btn-set-speed').on('click', function() {
    if (!currentRoomId) {
      showToast('请先选择房间', 'error');
      return;
    }
    
    $.ajax({
      url: `${API_BASE}/ac/room/${currentRoomId}/status`,
      method: 'GET',
      success: function(statusData) {
        if (!statusData.acOn) {
          showToast('请先开启空调', 'error');
          return;
        }
        
        const speed = $('#speed-select').val();
        if (!speed) {
          showToast('请选择风速', 'error');
          return;
        }
        
        $.ajax({
          url: `${API_BASE}/ac/room/${currentRoomId}/speed?fanSpeed=${speed}`,
          method: 'PUT',
          success: function(data) {
            showToast(data.message || '风速已设置', 'success');
            isUserEditingSpeed = false;
            loadRoomStatus(currentRoomId);
            loadUsageStats(currentRoomId);
          },
          error: function(xhr) {
            const data = xhr.responseJSON || {};
            showToast(data.error || '设置失败', 'error');
          }
        });
      },
      error: function() {
        showToast('检查空调状态失败', 'error');
      }
    });
  });
  
  loadRooms();
});
