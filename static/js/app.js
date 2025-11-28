const roomsBody = document.getElementById("rooms-body");
const servingList = document.getElementById("serving-list");
const waitingList = document.getElementById("waiting-list");
const toastEl = document.getElementById("toast");
const checkoutResult = document.getElementById("checkout-result");
const adminResult = document.getElementById("admin-result");

const showToast = (message, type = "info") => {
  if (!toastEl) return;
  toastEl.textContent = message;
  toastEl.className = "";
  toastEl.classList.add("show", type);
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    toastEl.classList.remove("show");
  }, 3200);
};

const requestJson = async (url, options = {}) => {
  const opts = {
    headers: {},
    ...options,
  };

  if (opts.body && !(opts.body instanceof FormData)) {
    opts.headers["Content-Type"] = "application/json";
  }

  const res = await fetch(url, opts);
  let data = null;
  try {
    data = await res.json();
  } catch (_) {
    data = null;
  }
  if (!res.ok) {
    throw new Error((data && data.error) || res.statusText);
  }
  return data;
};

const formatTemp = (value) =>
  typeof value === "number" ? value.toFixed(1) : "--";

const renderRooms = (rooms) => {
  if (!roomsBody) return;
  roomsBody.innerHTML = "";
  rooms.forEach((room) => {
    const tr = document.createElement("tr");
    tr.dataset.roomId = room.roomId ?? room.id ?? "";
    const fanSpeed = (room.fanSpeed || "--").toUpperCase();
    const target = room.targetTemp ?? "";
    tr.innerHTML = `
      <td>${room.roomId ?? room.id}</td>
      <td>${room.roomStatus || "--"}</td>
      <td>${formatTemp(room.currentTemp)}</td>
      <td>${target || "--"}</td>
      <td>${fanSpeed}</td>
      <td>${room.acOn ? "开启" : "关闭"}</td>
      <td>
        <div class="inline-actions">
          <button class="btn btn-start">开机</button>
          <button class="btn danger btn-stop">关机</button>
        </div>
      </td>
      <td>
        <div class="inline-field">
          <input type="number" step="0.5" class="input-temp" value="${target || ""}" placeholder="目标温度">
          <button class="btn btn-temp">设置</button>
        </div>
      </td>
      <td>
        <div class="inline-field">
          <select class="select-speed">
            <option value="LOW"${fanSpeed === "LOW" ? " selected" : ""}>LOW</option>
            <option value="MEDIUM"${fanSpeed === "MEDIUM" ? " selected" : ""}>MEDIUM</option>
            <option value="HIGH"${fanSpeed === "HIGH" ? " selected" : ""}>HIGH</option>
          </select>
          <button class="btn btn-speed">调整</button>
        </div>
      </td>
    `;
    roomsBody.appendChild(tr);
  });
};

const refreshRooms = async () => {
  try {
    const rooms = await requestJson("/monitor/status");
    renderRooms(rooms);
  } catch (err) {
    showToast(err.message, "error");
  }
};

const renderQueues = (data) => {
  if (!servingList || !waitingList) return;
  servingList.innerHTML = "";
  waitingList.innerHTML = "";
  data.servingQueue.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `房间 ${item.roomId} · 风速 ${item.fanSpeed} · 服务 ${Math.round(
      item.servingSeconds || 0
    )}s`;
    servingList.appendChild(li);
  });
  data.waitingQueue.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `房间 ${item.roomId} · 风速 ${item.fanSpeed} · 等待 ${Math.round(
      item.waitingSeconds || 0
    )}s`;
    waitingList.appendChild(li);
  });
};

const refreshQueues = async () => {
  try {
    const data = await requestJson("/monitor/status");
    renderQueues(data);
  } catch (err) {
    showToast(err.message, "error");
  }
};

const roomsTable = document.getElementById("rooms-table");
roomsTable?.addEventListener("click", async (event) => {
  const target = event.target;
  const row = target.closest("tr[data-room-id]");
  if (!row) {
    return;
  }
  const roomId = row.dataset.roomId;
  try {
    if (target.classList.contains("btn-start")) {
      await requestJson(`/ac/power`, { 
        method: "POST",
        body: JSON.stringify({ roomId: parseInt(roomId) })
      });
      showToast(`房间 ${roomId} 空调已开启`, "success");
    } else if (target.classList.contains("btn-stop")) {
      await requestJson(`/ac/power/off`, { 
        method: "POST",
        body: JSON.stringify({ roomId: parseInt(roomId) })
      });
      showToast(`房间 ${roomId} 空调已关闭`, "success");
    } else if (target.classList.contains("btn-temp")) {
      const input = row.querySelector(".input-temp");
      const targetTemp = input?.value;
      if (!targetTemp) {
        showToast("请输入目标温度", "error");
        return;
      }
      await requestJson(`/ac/temp`, {
        method: "POST",
        body: JSON.stringify({ roomId: parseInt(roomId), targetTemp: parseFloat(targetTemp) })
      });
      showToast(`房间 ${roomId} 温度已更新`, "success");
    } else if (target.classList.contains("btn-speed")) {
      const select = row.querySelector(".select-speed");
      const fanSpeed = select?.value;
      await requestJson(
        `/ac/speed`,
        { 
          method: "POST",
          body: JSON.stringify({ roomId: parseInt(roomId), fanSpeed: fanSpeed })
        }
      );
      showToast(`房间 ${roomId} 风速已调整为 ${fanSpeed}`, "success");
    } else {
      return;
    }
    await refreshRooms();
    await refreshQueues();
  } catch (err) {
    showToast(err.message, "error");
  }
});

document.getElementById("btn-refresh-rooms")?.addEventListener("click", refreshRooms);
document.getElementById("btn-refresh-queues")?.addEventListener("click", refreshQueues);

const checkinForm = document.getElementById("checkin-form");
checkinForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(checkinForm);
  const payload = Object.fromEntries(formData.entries());
  payload.roomId = Number(payload.roomId);
  try {
    const res = await requestJson("/hotel/checkin", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast(res.message || "入住成功", "success");
    checkinForm.reset();
    await refreshRooms();
  } catch (err) {
    showToast(err.message, "error");
  }
});

const checkoutForm = document.getElementById("checkout-form");
checkoutForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(checkoutForm);
  const roomId = formData.get("roomId");
  try {
    const res = await requestJson(`/hotel/checkout/${roomId}`, {
      method: "POST",
    });
    showToast("退房完成，账单已生成", "success");
    checkoutResult.textContent = JSON.stringify(res, null, 2);
    checkoutForm.reset();
    await refreshRooms();
    await refreshQueues();
  } catch (err) {
    showToast(err.message, "error");
  }
});

const maintenanceForm = document.getElementById("maintenance-form");
maintenanceForm?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!target.matches("button[data-action]")) return;
  event.preventDefault();
  const roomIdInput = document.getElementById("maintenance-room-id");
  const roomId = roomIdInput?.value;
  if (!roomId) {
    showToast("请输入房间号", "error");
    return;
  }
  const action = target.dataset.action;
  const endpoint = action === "offline" ? "offline" : "online";
  try {
    // 注意：后端可能没有这个路由，需要检查
    const res = await requestJson(`/admin/rooms/${roomId}/${endpoint}`, {
      method: "POST",
    });
    showToast(res.message || "操作成功", "success");
    adminResult.textContent = JSON.stringify(res.room || res.schedule || res, null, 2);
    await refreshRooms();
  } catch (err) {
    showToast(err.message, "error");
  }
});

document.getElementById("btn-force-rotation")?.addEventListener("click", async () => {
  try {
    // 注意：后端可能没有这个路由，需要检查
    const res = await requestJson("/admin/maintenance/force-rotation", {
      method: "POST",
    });
    adminResult.textContent = JSON.stringify(res.schedule, null, 2);
    showToast(res.message, "success");
    await refreshQueues();
  } catch (err) {
    showToast(err.message, "error");
  }
});

document.getElementById("btn-simulate-temp")?.addEventListener("click", async () => {
  try {
    // 注意：后端可能没有这个路由，需要检查
    const res = await requestJson("/admin/maintenance/simulate-temperature", {
      method: "POST",
    });
    adminResult.textContent = JSON.stringify(res, null, 2);
    showToast(res.message || "温度已模拟更新", "success");
    await refreshRooms();
  } catch (err) {
    showToast(err.message, "error");
  }
});

refreshRooms();
refreshQueues();
setInterval(refreshQueues, 5000);

