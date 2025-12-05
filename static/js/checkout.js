// Check-out Logic

function performCheckout() {
  const roomId = document.getElementById('roomIdInput').value;
  if (!roomId) {
      alert("请输入房间号");
      return;
  }

  axios.post(`/hotel/checkout/${roomId}`)
      .then(response => {
          renderInvoice(response.data);
      })
      .catch(error => {
          console.error(error);
          alert("退房失败: " + (error.response?.data?.error || error.message));
      });
}

function renderInvoice(data) {
  // data 结构对应 CheckoutResponse
  const customer = data.customer;
  const bill = data.bill;
  const details = data.detailBill;

  // 1. 显示容器
  document.getElementById('invoice-container').style.display = 'flex';

  // 2. 填充头部信息
  document.getElementById('bill-date').innerText = new Date().toLocaleDateString();
  document.getElementById('bill-id').innerText = Date.now().toString().slice(-6); // 模拟单号

  // 3. 客户信息
  if (customer) {
      document.getElementById('customer-info').innerHTML = `
          <div><strong>客户姓名:</strong> ${customer.name}</div>
          <div><strong>身份证号:</strong> ${customer.idCard || '--'}</div>
          <div><strong>联系电话:</strong> ${customer.phoneNumber || '--'}</div>
      `;
  }

  // 4. 汇总数据
  if (bill) {
      document.getElementById('stay-days').innerText = bill.duration + " 天";
      document.getElementById('room-fee').innerText = bill.roomFee.toFixed(2);
      document.getElementById('ac-fee').innerText = bill.acFee.toFixed(2);
      
      const total = (bill.roomFee + bill.acFee).toFixed(2);
      document.getElementById('total-amount').innerText = total;
  }

  // 5. 详单表格
  const tbody = document.getElementById('detail-list');
  tbody.innerHTML = '';

  if (details && details.length > 0) {
      details.forEach(item => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
              <td>${item.roomId}</td>
              <td>${formatTime(item.startTime)}</td>
              <td>${formatTime(item.endTime)}</td>
              <td>${item.duration}</td>
              <td>${item.fanSpeed}</td>
              <td>${item.rate}</td>
              <td>¥ ${(item.acFee || 0).toFixed(2)}</td>
              <td>¥ ${(item.roomFee || 0).toFixed(2)}</td>
              <td class="fw-bold text-primary">¥ ${(item.fee || 0).toFixed(2)}</td>
          `;
          tbody.appendChild(tr);
      });
  } else {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#999">无详细消费记录</td></tr>';
  }
}

function formatTime(isoStr) {
  if (!isoStr) return '--';
  const d = new Date(isoStr);
  return d.toLocaleString('zh-CN', { hour12: false });
}