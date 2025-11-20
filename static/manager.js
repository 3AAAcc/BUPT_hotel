const API_BASE = '/api';

async function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `show ${type}`;
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

function formatDate(dateStr) {
  if (!dateStr) return null;
  return new Date(dateStr).toISOString().split('T')[0];
}

function getQueryParams() {
  const start = document.getElementById('start-date').value;
  const end = document.getElementById('end-date').value;
  const params = new URLSearchParams();
  if (start) params.append('start', new Date(start).toISOString());
  if (end) params.append('end', new Date(end + 'T23:59:59').toISOString());
  return params.toString();
}

async function loadOverview() {
  try {
    const query = getQueryParams();
    const res = await fetch(`${API_BASE}/reports/overview${query ? '?' + query : ''}`);
    const data = await res.json();
    
    const container = document.getElementById('overview-content');
    container.innerHTML = `
      <div class="stat-card">
        <label>总房间数</label>
        <div class="value">${data.roomStats?.total || 0}</div>
      </div>
      <div class="stat-card">
        <label>已入住</label>
        <div class="value">${data.roomStats?.occupied || 0}</div>
        <div class="sub-value">入住率: ${((data.roomStats?.occupancyRate || 0) * 100).toFixed(1)}%</div>
      </div>
      <div class="stat-card">
        <label>维修中</label>
        <div class="value">${data.roomStats?.maintenance || 0}</div>
      </div>
      <div class="stat-card">
        <label>住宿费收入</label>
        <div class="value">¥${(data.revenue?.roomFee || 0).toFixed(2)}</div>
      </div>
      <div class="stat-card">
        <label>空调费收入</label>
        <div class="value">¥${(data.revenue?.acFee || 0).toFixed(2)}</div>
      </div>
      <div class="stat-card">
        <label>总收入</label>
        <div class="value">¥${(data.revenue?.total || 0).toFixed(2)}</div>
      </div>
      <div class="stat-card">
        <label>账单数量</label>
        <div class="value">${data.billing?.billCount || 0}</div>
        <div class="sub-value">平均空调费: ¥${(data.billing?.avgAcFee || 0).toFixed(2)}</div>
      </div>
    `;
  } catch (error) {
    showToast('加载运营概览失败', 'error');
  }
}

async function loadUsageStats() {
  try {
    const query = getQueryParams();
    const res = await fetch(`${API_BASE}/reports/ac-usage${query ? '?' + query : ''}`);
    const data = await res.json();
    
    const container = document.getElementById('usage-content');
    container.innerHTML = `
      <div class="overview-grid" style="margin-bottom: 20px;">
        <div class="stat-card">
          <label>总使用次数</label>
          <div class="value">${data.totalSessions || 0}</div>
        </div>
        <div class="stat-card">
          <label>总使用时长</label>
          <div class="value">${data.totalDurationMinutes || 0}</div>
          <div class="sub-value">分钟</div>
        </div>
        <div class="stat-card">
          <label>总费用</label>
          <div class="value">¥${(data.totalCost || 0).toFixed(2)}</div>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>风速</th>
              <th>使用时长（分钟）</th>
              <th>费用</th>
            </tr>
          </thead>
          <tbody>
            ${(data.byFanSpeed || []).map(item => `
              <tr>
                <td>${item.fanSpeed}</td>
                <td>${item.durationMinutes}</td>
                <td>¥${item.cost.toFixed(2)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (error) {
    showToast('加载使用统计失败', 'error');
  }
}

async function loadRevenue() {
  try {
    const days = parseInt(document.getElementById('days-select').value) || 7;
    const res = await fetch(`${API_BASE}/reports/daily-revenue?days=${days}`);
    const data = await res.json();
    
    const container = document.getElementById('revenue-content');
    if (data.length === 0) {
      container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">暂无数据</p>';
      return;
    }
    
    container.innerHTML = `
      <div class="revenue-list">
        ${data.map(item => `
          <div class="revenue-item">
            <div>
              <div class="date">${item.date}</div>
              <div class="breakdown">
                住宿费: ¥${item.roomFee.toFixed(2)} · 空调费: ¥${item.acFee.toFixed(2)}
              </div>
            </div>
            <div class="amount">¥${item.total.toFixed(2)}</div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (error) {
    showToast('加载营收趋势失败', 'error');
  }
}

document.getElementById('btn-apply-filter').addEventListener('click', () => {
  loadOverview();
  loadUsageStats();
});

document.getElementById('btn-reset-filter').addEventListener('click', () => {
  document.getElementById('start-date').value = '';
  document.getElementById('end-date').value = '';
  loadOverview();
  loadUsageStats();
});

document.getElementById('btn-refresh-overview').addEventListener('click', loadOverview);
document.getElementById('btn-refresh-usage').addEventListener('click', loadUsageStats);
document.getElementById('btn-refresh-revenue').addEventListener('click', loadRevenue);
document.getElementById('days-select').addEventListener('change', loadRevenue);

loadOverview();
loadUsageStats();
loadRevenue();

