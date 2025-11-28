// Dashboard Logic

document.addEventListener('DOMContentLoaded', () => {
    startMonitoring();
});

function startMonitoring() {
    // 立即加载一次
    loadData();
    // 每秒刷新一次 (为了让时间跳动更流畅)
    setInterval(loadData, 1000);
}

function loadData() {
    axios.get('/monitor/status')
        .then(response => {
            renderDashboard(response.data);
        })
        .catch(err => console.error("监控数据获取失败", err));
}

function renderDashboard(data) {
    // 1. 更新顶部系统指标
    document.getElementById('sys-capacity').innerText = data.capacity;
    document.getElementById('sys-timeslice').innerText = data.timeSlice;

    // 2. 渲染服务队列
    const servingList = document.getElementById('serving-list');
    document.getElementById('serving-count').innerText = data.servingQueue.length;
    servingList.innerHTML = data.servingQueue.map(item => createServingCard(item, data.timeSlice)).join('');

    // 3. 渲染等待队列
    const waitingList = document.getElementById('waiting-list');
    document.getElementById('waiting-count').innerText = data.waitingQueue.length;
    waitingList.innerHTML = data.waitingQueue.map(item => createWaitingCard(item)).join('');
}

function createServingCard(item, maxTime) {
    // 简单的进度条逻辑：假设服务时间不超过时间片太多
    const percent = Math.min(100, (item.servingSeconds / maxTime) * 100);
    
    return `
        <div class="mon-card serving-card">
            <div class="card-top">
                <span class="room-id">Room ${item.roomId}</span>
                <span class="temp-info">
                    <i class="fa-solid fa-temperature-arrow-down"></i> ${item.targetTemp}°C
                </span>
            </div>
            <div class="card-mid">
                <span class="tag">${item.fanSpeed}</span>
                <span class="tag">${item.mode}</span>
            </div>
            <div class="time-info">
                <small>已服务: ${item.servingSeconds.toFixed(0)}s</small>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: ${percent}%"></div>
            </div>
        </div>
    `;
}

function createWaitingCard(item) {
    // 计算优先级显示 (简单的映射，或者直接显示风速)
    let priorityColor = '#94a3b8';
    if(item.fanSpeed === 'HIGH') priorityColor = '#e74c3c'; // 高风红
    if(item.fanSpeed === 'MEDIUM') priorityColor = '#f39c12'; // 中风橙
    
    return `
        <div class="mon-card waiting-card">
            <div>
                <div class="room-id">Room ${item.roomId}</div>
                <div style="margin-top:5px">
                    <span class="tag" style="color:${priorityColor}">${item.fanSpeed}</span>
                </div>
            </div>
            <div class="text-right">
                <div class="wait-time">${item.waitingSeconds.toFixed(0)}s</div>
                <small style="color:#64748b">等待中</small>
            </div>
        </div>
    `;
}