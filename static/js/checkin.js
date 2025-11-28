// Check-in Logic (入住办理逻辑)

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('checkin-form');
  
  if (form) {
      form.addEventListener('submit', handleCheckIn);
  }
});

function handleCheckIn(event) {
  // 1. 阻止表单默认提交（防止页面刷新）
  event.preventDefault();

  // 2. 获取按钮并添加加载状态（提升体验）
  const btn = document.querySelector('.btn-submit');
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 处理中...';

  // 3. 收集表单数据
  const formData = {
      roomId: document.getElementById('roomId').value,
      idCard: document.getElementById('idCard').value,
      name: document.getElementById('name').value,
      phoneNumber: document.getElementById('phoneNumber').value
  };

  // 4. 发送请求给后端
  // 注意：这里调用的是 hotel_controller.py 里的 /hotel/checkin
  axios.post('/hotel/checkin', formData)
      .then(response => {
          // 成功：提示并跳转
          alert("✅ " + (response.data.message || "入住办理成功！"));
          window.location.href = '/reception'; // 跳回前台大厅看状态
      })
      .catch(error => {
          // 失败：显示错误信息
          console.error(error);
          const errMsg = error.response?.data?.error || "服务器连接失败";
          alert("❌ 办理失败: " + errMsg);
      })
      .finally(() => {
          // 恢复按钮状态
          btn.disabled = false;
          btn.innerHTML = originalText;
      });
}