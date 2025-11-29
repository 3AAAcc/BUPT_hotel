// Customer Logic (支持制冷/制热双模式)

let currentRoomId = null;
let pollInterval = null;
// 定义温度范围常量
const LIMITS = {
    'COOLING': { min: 18, max: 28 },
    'HEATING': { min: 18, max: 25 } // 制热最高25
};
let currentMode = 'COOLING'; // 默认

document.addEventListener('DOMContentLoaded', () => { initRoomId(); });

function initRoomId() {
    const urlParams = new URLSearchParams(window.location.search);
    currentRoomId = urlParams.get('roomId') || localStorage.getItem('lastRoomId');
    
    if (!currentRoomId) {
        currentRoomId = prompt("请输入当前房间号 (1-5):", "1");
}

    if (currentRoomId) {
        localStorage.setItem('lastRoomId', currentRoomId);
        document.getElementById('room-id-display').innerText = currentRoomId;
        // 在浏览器标签上区分不同房间
        try {
            const baseTitle = document.title.split('|')[0].trim() || '客房温控系统';
            document.title = `${baseTitle} | 房间 ${currentRoomId}`;
        } catch (e) {
            document.title = `客房温控系统 | 房间 ${currentRoomId}`;
        }
        updateState();
        pollInterval = setInterval(updateState, 1000);
    } else {
        alert("未指定房间号！");
    }
}
  
function updateState() {
    if (!currentRoomId) return;
    axios.get(`/ac/state?roomId=${currentRoomId}`)
        .then(res => renderUI(res.data))
        .catch(err => {
            console.error(err);
            document.getElementById('ac-status').innerText = "连接断开";
        });
}

function renderUI(data) {
    // 1. 基本数据
    const isOn = data.ac_on;
    const modeVal = data.ac_mode || 'COOLING';
    currentMode = modeVal; // 更新全局模式变量
    const queueState = data.queueState || data.queue_state || 'IDLE';

    // 2. 状态灯
    const statusText = document.getElementById('ac-status');
    const badge = document.getElementById('ac-status-badge');
    if (isOn) {
        statusText.innerText = "运行中";
        badge.style.color = "#2ecc71";
    } else {
        statusText.innerText = "已关机";
        badge.style.color = "#95a5a6";
    }

    // 2.1 队列状态显示（服务 / 等待 / 回温待机 / 空闲）
    const queueBadge = document.getElementById('queue-status-badge');
    const queueLabel = document.getElementById('queue-state');
    if (queueBadge && queueLabel) {
        let text = '队列: 空闲';
        let color = '#95a5a6';
        const qs = String(queueState || '').toUpperCase();
        if (qs === 'SERVING') { text = '队列: 服务中'; color = '#2ecc71'; }
        else if (qs === 'WAITING') { text = '队列: 等待中'; color = '#f1c40f'; }
        else if (qs === 'PAUSED') { text = '队列: 回温待机'; color = '#3498db'; }
        queueLabel.innerText = text;
        queueBadge.style.color = color;
    }

    // 3. 温度显示
    const cTemp = data.current_temp ?? data.currentTemp ?? '--';
    const tTemp = data.target_temp ?? data.targetTemp ?? '--';
    document.getElementById('current-temp').innerText = cTemp;
    document.getElementById('target-temp').innerText = tTemp;

    // 4. 模式与风速文字
    const modeMap = { 'COOLING': '制冷', 'HEATING': '制热' };
    const speedMap = { 'LOW': '低', 'MEDIUM': '中', 'HIGH': '高' };
    document.getElementById('mode').innerText = modeMap[modeVal] || modeVal;
    document.getElementById('fan-speed').innerText = speedMap[data.fan_speed] || data.fan_speed;

    // 5. 费用
    const total = data.total_cost || data.totalCost || 0.0;
    const current = data.current_cost || data.currentCost || 0.0;
    document.getElementById('total-fee').innerText = parseFloat(total).toFixed(2);
    document.getElementById('cost').innerText = parseFloat(current).toFixed(2);

    // === 6. UI 主题色与按钮高亮 (核心修改) ===
    const circle = document.querySelector('.temp-circle');
    const btnCool = document.getElementById('btn-mode-cool');
    const btnHeat = document.getElementById('btn-mode-heat');

    // 重置按钮样式
    btnCool.classList.remove('active-mode-cool');
    btnHeat.classList.remove('active-mode-heat');

    if (modeVal === 'HEATING') {
        // 制热：红色主题
        if(isOn) circle.style.borderColor = '#ff6b6b'; // 红圈
        btnHeat.classList.add('active-mode-heat');
    } else {
        // 制冷：蓝色主题
        if(isOn) circle.style.borderColor = '#4facfe'; // 蓝圈
        btnCool.classList.add('active-mode-cool');
    }
    
    if(!isOn) circle.style.borderColor = '#ffffff'; // 关机白圈
}

// === 控制指令 ===

function powerOn() {
    axios.post('/ac/power', { roomId: currentRoomId }).then(updateState);
}
function powerOff() {
    axios.post('/ac/power/off', { roomId: currentRoomId }).then(updateState);
}

function changeTemp(delta) {
    let currentTarget = parseFloat(document.getElementById('target-temp').innerText);
    if (isNaN(currentTarget)) return;

    const newTemp = currentTarget + delta;
    
    // === 核心修改：根据模式限制温度 ===
    const limit = LIMITS[currentMode] || { min: 18, max: 28 };
    
    if (newTemp < limit.min || newTemp > limit.max) {
        alert(`当前模式(${currentMode}) 温度范围: ${limit.min} ~ ${limit.max}°C`);
      return;
    }
    
    axios.post('/ac/temp', { roomId: currentRoomId, targetTemp: newTemp })
        .then(() => document.getElementById('target-temp').innerText = newTemp)
        .catch(err => alert("调温失败: " + err.response?.data?.error));
        }
        
function changeSpeed(speed) {
    axios.post('/ac/speed', { roomId: currentRoomId, fanSpeed: speed }).then(updateState);
}

function changeMode(mode) {
    axios.post('/ac/mode', { roomId: currentRoomId, mode: mode })
        .then(() => {
            // 切换模式后，立即刷新一下状态，因为目标温度会变
            setTimeout(updateState, 200); 
        })
        .catch(err => alert("切换模式失败"));
}
