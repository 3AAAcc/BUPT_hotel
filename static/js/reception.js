/**
 * Reception Logic (前台大厅逻辑)
 * 负责轮询房间状态并渲染卡片
 */

// 核心渲染函数
function loadRoomStatus() {
  axios.get('/hotel/rooms')
      .then(response => {
          const rooms = response.data;
          const container = document.getElementById('room-list');
          
          // 如果后端没有返回数据，显示提示
          if (!rooms || rooms.length === 0) {
              container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #999; padding: 20px;">暂无房间数据</div>';
              return;
          }

          // 使用一个字符串变量构建 HTML，而不是在循环里反复操作 DOM (提升性能，减少闪烁感)
          let htmlContent = '';

          rooms.forEach(room => {
              // 1. 判断状态
              const isOccupied = (room.status === 'OCCUPIED');
              const statusClass = isOccupied ? 'status-OCCUPIED' : 'status-AVAILABLE';
              
              // 2. 生成按钮逻辑 (退房 vs 入住)
              // 注意：这里带上了 roomId 参数，方便跳转后自动填入
              let actionBtn = '';
              if (isOccupied) {
                  actionBtn = `
                      <a href="/reception/checkout?roomId=${room.id}" class="btn-card-action btn-checkout">
                          <i class="fa-solid fa-right-from-bracket"></i> 办理退房
                      </a>`;
              } else {
                  actionBtn = `
                      <a href="/reception/checkin?roomId=${room.id}" class="btn-card-action btn-checkin">
                          <i class="fa-solid fa-key"></i> 办理入住
                      </a>`;
              }

              // 3. 生成中间信息 (客户名 vs 空闲提示)
              // 注意：Room.to_dict() 返回的是 customerName (驼峰命名)
              const customerName = room.customerName || room.customer_name;
              const customerInfo = isOccupied 
                  ? `<div class="customer-name" title="${customerName}">
                          <i class="fa-solid fa-user"></i> ${customerName || '未知客户'}
                     </div>` 
                  : `<div class="status-text"><i class="fa-regular fa-circle-check"></i> 当前空闲</div>`;

              // 4. 处理温度显示 (如果为 null 显示 --)
              // 注意：Room.to_dict() 返回的是 currentTemp (驼峰命名)，不是 current_temp
              const currentTemp = (room.currentTemp !== null && room.currentTemp !== undefined) 
                                  ? room.currentTemp 
                                  : '--';

              // 5. 拼接卡片 HTML (严格匹配 reception.css 的类名)
              htmlContent += `
                  <div class="room-card ${statusClass}">
                      <div class="room-header">
                          <span class="room-id">Room ${room.id}</span>
                          <span class="temp-badge">
                              <i class="fa-solid fa-temperature-half"></i> ${currentTemp}°C
                          </span>
                      </div>
                      <div class="room-body">
                          ${customerInfo}
                      </div>
                      <div class="room-actions">
                          ${actionBtn}
                      </div>
                  </div>
              `;
          });

          // 一次性更新页面
          container.innerHTML = htmlContent;
      })
      .catch(error => {
          console.error('获取房间状态失败:', error);
          // 这里不弹窗报错，以免打扰用户，但在控制台记录
      });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
  // 1. 立即加载一次
  loadRoomStatus();

  // 2. 开启定时轮询 (设置为 5000 毫秒 = 5秒)
  // 5秒是一个比较合理的间隔，既能看到变化，又不会觉得页面在乱跳
  setInterval(loadRoomStatus, 5000);
});