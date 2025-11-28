// Admin Report Logic

// 1. 查询房间详单
function queryRoomReport() {
  const roomId = document.getElementById('roomReportId').value;
  if (!roomId) return alert("请输入房间号");

  renderLoading('room-tbody', 7);

  axios.get(`/report/room?roomId=${roomId}`)
      .then(res => {
          const data = res.data;
          const tbody = document.getElementById('room-tbody');
          tbody.innerHTML = '';

          if (!data || data.length === 0) {
              tbody.innerHTML = '<tr><td colspan="7" class="text-center">该房间无记录</td></tr>';
              return;
          }

          data.forEach(row => {
              const isSummary = row.type === 'SUMMARY';
              const acFee = (row.acFee || 0).toFixed(2);
              const roomFee = (row.roomFee || 0).toFixed(2);
              const totalFee = (row.fee || row.acFee || 0).toFixed(2);
              
              if (isSummary) {
                  // 汇总行
                  tbody.innerHTML += `
                      <tr class="table-info">
                          <td><strong>${row.roomId}</strong></td>
                          <td colspan="2" class="text-center"><strong>汇总</strong></td>
                          <td>--</td>
                          <td><strong>${row.fanSpeed}</strong></td>
                          <td>--</td>
                          <td>
                              <div class="fee-breakdown">
                                  <span class="text-muted small">空调费: ¥${acFee}</span><br>
                                  <span class="text-muted small">房费: ¥${roomFee}</span><br>
                                  <span class="fw-bold text-primary">总计: ¥${totalFee}</span>
                              </div>
                          </td>
                      </tr>
                  `;
              } else {
                  // 普通详单行（只显示空调费）
                  tbody.innerHTML += `
                      <tr>
                          <td>${row.roomId}</td>
                          <td>${formatTime(row.startTime)}</td>
                          <td>${formatTime(row.endTime)}</td>
                          <td>${row.duration || '--'}</td>
                          <td>${row.fanSpeed || '--'}</td>
                          <td>${row.rate || '--'}</td>
                          <td class="fw-bold text-primary">¥${acFee}</td>
                      </tr>
                  `;
              }
          });
      })
      .catch(err => handleError(err, 'room-tbody', 7));
}

// 2. 查询日报表
function queryDailyReport() {
  const date = document.getElementById('dailyDate').value;
  if (!date) return alert("请选择日期");

  renderLoading('daily-tbody', 7);

  axios.get(`/report/daily?date=${date}`)
      .then(res => renderAggregatedTable(res.data, 'daily-tbody'))
      .catch(err => handleError(err, 'daily-tbody', 7));
}

// 3. 查询周报表
function queryWeeklyReport() {
  const date = document.getElementById('weeklyDate').value;
  if (!date) return alert("请选择开始日期");

  renderLoading('weekly-tbody', 7);

  axios.get(`/report/weekly?startDate=${date}`)
      .then(res => renderAggregatedTable(res.data, 'weekly-tbody'))
      .catch(err => handleError(err, 'weekly-tbody', 7));
}

// 通用渲染函数 (日报和周报结构一样)
function renderAggregatedTable(data, tbodyId) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = '';

  if (!data || data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center">无数据</td></tr>';
      return;
  }

  data.forEach(row => {
      // 显示房费和空调费的明细
      const acFee = (row.acFee || 0).toFixed(2);
      const roomFee = (row.roomFee || 0).toFixed(2);
      const totalFee = (row.totalFee || 0).toFixed(2);
      
      tbody.innerHTML += `
          <tr>
              <td><strong>${row.roomId}</strong></td>
              <td>${row.usageCount}</td>
              <td>${(row.totalDuration / 60).toFixed(1)}</td>
              <td class="fw-bold text-success">
                  <div class="fee-breakdown">
                      <span class="text-muted small">空调: ¥${acFee}</span><br>
                      <span class="text-muted small">房费: ¥${roomFee}</span><br>
                      <span class="fw-bold">总计: ¥${totalFee}</span>
                  </div>
              </td>
              <td>${row.dispatchCount}</td>
              <td>${row.recordCount}</td>
              <td>${row.avgTempDiff ? row.avgTempDiff.toFixed(1) : '--'}</td>
          </tr>
      `;
  });
}

// 工具函数
function renderLoading(tbodyId, cols) {
  document.getElementById(tbodyId).innerHTML = 
      `<tr><td colspan="${cols}" class="text-center py-4"><i class="fa-solid fa-spinner fa-spin text-primary"></i> 数据加载中...</td></tr>`;
}

function handleError(err, tbodyId, cols) {
  console.error(err);
  document.getElementById(tbodyId).innerHTML = 
      `<tr><td colspan="${cols}" class="text-center text-danger">查询失败: ${err.response?.data?.error || err.message}</td></tr>`;
}

function formatTime(isoStr) {
  if (!isoStr) return '--';
  return new Date(isoStr).toLocaleString('zh-CN', { hour12: false });
}