const API_BASE = '/api';

function showToast(message, type = 'info') {
  const $toast = $('#toast');
  $toast.text(message);
  $toast.attr('class', `show ${type}`);
  setTimeout(() => {
    $toast.removeClass('show');
  }, 3000);
}

function showAlert(message, type = 'success') {
  const title = type === 'success' ? '入住成功' : '入住失败';
  const icon = type === 'success' ? '✓' : '✗';
  alert(`${icon} ${title}\n\n${message}`);
}

function loadAvailableRooms() {
  $.ajax({
    url: `${API_BASE}/hotel/rooms/available`,
    method: 'GET',
    success: function(rooms) {
      const $checkinSelect = $('#checkin-room-id');
      const $tbody = $('#rooms-body');
      
      $checkinSelect.html('<option value="">请选择房间</option>');
      $tbody.empty();
      
      $.each(rooms, function(index, room) {
        if (room.status === 'AVAILABLE') {
          $checkinSelect.append($('<option>').val(room.id).text(`房间 ${room.id}`));
          
          const $tr = $('<tr>').html(`
            <td>${room.id}</td>
            <td><span class="status-badge status-available">空闲</span></td>
            <td>
              <button class="btn btn-primary btn-sm" onclick="quickCheckin(${room.id})">选择此房间</button>
            </td>
          `);
          $tbody.append($tr);
        }
      });
    },
    error: function() {
      showToast('加载可用房间失败', 'error');
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

$(document).ready(function() {
  $('#checkin-form').on('submit', function(e) {
    e.preventDefault();
    const roomId = parseInt($('#checkin-room-id').val());
    const name = $('#checkin-name').val();
    const idCard = $('#checkin-id-card').val();
    const phone = $('#checkin-phone').val();
    
    if (!roomId || !name) {
      showToast('请填写必填项', 'error');
      showAlert('请填写必填项（房间号和客户姓名）', 'error');
      return;
    }
    
    $.ajax({
      url: `${API_BASE}/hotel/checkin`,
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ roomId, name, idCard, phoneNumber: phone }),
      success: function(data) {
        const message = data.message || '入住成功';
        showToast(message, 'success');
        
        const alertMessage = `房间号：${roomId}\n客户姓名：${name}\n${idCard ? '身份证号：' + idCard + '\n' : ''}${phone ? '联系电话：' + phone + '\n' : ''}\n\n${message}`;
        showAlert(alertMessage, 'success');
        
        $('#checkin-form')[0].reset();
        loadAvailableRooms();
      },
      error: function(xhr) {
        const data = xhr.responseJSON || {};
        const errorMsg = data.error || '入住失败';
        showToast(errorMsg, 'error');
        showAlert(errorMsg, 'error');
      }
    });
  });
  
  $('#btn-refresh-rooms').on('click', loadAvailableRooms);
  
  window.quickCheckin = function(roomId) {
    $('#checkin-room-id').val(roomId);
    $('#checkin-name').focus();
  };
  
  // 从URL参数中获取房间号
  function initFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = urlParams.get('roomId');
    if (roomId) {
      $('#checkin-room-id').val(roomId);
      $('#checkin-name').focus();
    }
  }
  
  loadAvailableRooms();
  initFromUrl();
});
