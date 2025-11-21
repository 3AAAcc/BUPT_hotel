const API_BASE = '/api';

function showToast(message, type = 'info') {
  const $toast = $('#toast');
  $toast.text(message);
  $toast.attr('class', `show ${type}`);
  setTimeout(() => {
    $toast.removeClass('show');
  }, 3000);
}

const $billRoomSelect = $('#bill-room-id');

function loadAllRooms() {
  $.ajax({
    url: `${API_BASE}/monitor/roomstatus`,
    method: 'GET',
    success: function(rooms) {
      const $tbody = $('#rooms-body');
      
      if ($billRoomSelect.length) {
        $billRoomSelect.html('<option value="">请选择房间</option>');
      }
      if ($tbody.length) {
        $tbody.empty();
      }
      
      function formatDateTime(dateStr) {
        if (!dateStr) return '--';
        try {
          let date;
          if (dateStr.endsWith('Z')) {
            date = new Date(dateStr);
          } else if (dateStr.includes('T') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
            date = new Date(dateStr + 'Z');
          } else {
            date = new Date(dateStr);
          }
          return date.toLocaleString('zh-CN', { 
            timeZone: 'Asia/Shanghai',
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit', 
            hour: '2-digit', 
            minute: '2-digit' 
          });
        } catch {
          return dateStr;
        }
      }
      
      $.each(rooms, function(index, room) {
        if ($billRoomSelect.length) {
          $billRoomSelect.append($('<option>').val(room.roomId).text(`房间 ${room.roomId}`));
        }
        
        if (!$tbody.length) return;
        
        const statusClass = room.roomStatus === 'OCCUPIED' ? 'status-occupied' : 
                           room.roomStatus === 'MAINTENANCE' ? 'status-maintenance' : 'status-available';
        
        let actionContent = '--';
        if (room.roomStatus === 'OCCUPIED') {
          actionContent = `<a href="/reception/checkout?roomId=${room.roomId}" class="btn btn-danger btn-sm" style="text-decoration: none; display: inline-block;">退房</a>`;
        } else if (room.roomStatus === 'AVAILABLE') {
          actionContent = `<a href="/reception/checkin?roomId=${room.roomId}" class="btn btn-primary btn-sm" style="text-decoration: none; display: inline-block;">入住</a>`;
        } else if (room.roomStatus === 'MAINTENANCE') {
          actionContent = `<button class="btn btn-primary btn-sm" onclick="restoreRoom(${room.roomId})">恢复可用</button>`;
        }

        const $tr = $('<tr>').html(`
          <td>${room.roomId}</td>
          <td><span class="status-badge ${statusClass}">${getStatusText(room.roomStatus)}</span></td>
          <td>${room.customerName || '--'}</td>
          <td>${room.customerIdCard || '--'}</td>
          <td>${room.customerPhone || '--'}</td>
          <td>${formatDateTime(room.checkInTime)}</td>
          <td>${actionContent}</td>
        `);
        $tbody.append($tr);
      });
    },
    error: function() {
      showToast('加载房间状态失败', 'error');
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

function renderBills(bills = []) {
  const $container = $('#bills-result');
  if (!bills || bills.length === 0) {
    $container.addClass('show');
    $container.html('<p>未查询到账单数据。</p>');
    return;
  }

  function formatDate(value) {
    if (!value) return '--';
    try {
      let date;
      if (value.endsWith('Z')) {
        date = new Date(value);
      } else if (value.includes('T') && !value.includes('+') && !value.includes('-', 10)) {
        date = new Date(value + 'Z');
      } else {
        date = new Date(value);
      }
      return date.toLocaleString('zh-CN', {
        timeZone: 'Asia/Shanghai',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return value;
    }
  }

  const rows = bills.map(function(bill) {
    return `
      <tr>
        <td>${bill.id}</td>
        <td>${bill.roomId}</td>
        <td>${formatDate(bill.checkInTime)}</td>
        <td>${formatDate(bill.checkOutTime)}</td>
        <td>¥${(bill.roomFee || 0).toFixed(2)}</td>
        <td>¥${(bill.acFee || 0).toFixed(2)}</td>
        <td>¥${(bill.totalAmount || 0).toFixed(2)}</td>
        <td>${bill.status}</td>
      </tr>
    `;
  }).join('');

  $container.addClass('show');
  $container.html(`
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>账单ID</th>
            <th>房间号</th>
            <th>入住</th>
            <th>退房</th>
            <th>房费</th>
            <th>空调费</th>
            <th>总额</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `);
}

$(document).ready(function() {
  $('#btn-refresh-rooms').on('click', loadAllRooms);
  
  $('#bill-room-form').on('submit', function(e) {
    e.preventDefault();
    const roomId = parseInt($billRoomSelect.val());
    if (!roomId) {
      showToast('请选择房间', 'error');
      return;
    }
    
    $.ajax({
      url: `${API_BASE}/bills/room-id/${roomId}`,
      method: 'GET',
      success: function(data) {
        renderBills(data);
        showToast(`已展示房间 ${roomId} 的账单`, 'success');
      },
      error: function(xhr) {
        const data = xhr.responseJSON || {};
        showToast(data.error || '查询失败', 'error');
      }
    });
  });
  
  $('#btn-fetch-all-bills').on('click', function() {
    $.ajax({
      url: `${API_BASE}/bills`,
      method: 'GET',
      success: function(data) {
        renderBills(data);
        showToast('已加载所有账单', 'success');
      },
      error: function(xhr) {
        const data = xhr.responseJSON || {};
        showToast(data.error || '查询失败', 'error');
      }
    });
  });
  
  loadAllRooms();
});

window.restoreRoom = function(roomId) {
  if (!roomId) return;
  if (!confirm(`确认将房间 ${roomId} 从维修状态恢复为可用吗？`)) {
    return;
  }
  $.ajax({
    url: `${API_BASE}/admin/rooms/${roomId}/online`,
    method: 'POST',
    success: function(data) {
      showToast(data.message || '房间已恢复可用', 'success');
      loadAllRooms();
    },
    error: function(xhr) {
      const resp = xhr.responseJSON || {};
      showToast(resp.error || '恢复失败', 'error');
    }
  });
};
