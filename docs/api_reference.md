## 酒店空调系统 API 参考

所有接口默认前缀为 `http://<host>:8080/api`，响应均为 `application/json`，除 CSV 导出外。

---

### 通用返回字段

| 字段 | 说明 |
| --- | --- |
| `message` | 操作成功的提示语 |
| `error` | 发生错误时的描述 |

---

### 1. 入住 / 退房 `(/api/hotel)`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/hotel/available` | 返回可用房间 ID 列表 |
| GET | `/hotel/rooms/available` | 返回可用房间详细信息 |
| POST | `/hotel/checkin` | 办理入住 |
| POST | `/hotel/checkout/{roomId}` | 办理退房并返回账单 |

**办理入住**

- Body(JSON)：`{ "roomId": 1, "name": "张三", "idCard": "123", "phoneNumber": "138***" }`
- 成功返回：`{"message": "入住成功"}`

**办理退房**

- Path 参数：`roomId`
- 成功返回 `CheckoutResponse`：
  ```json
  {
    "detailBill": [
      {
        "roomId": 1,
        "startTime": "...",
        "endTime": "...",
        "duration": 30,
        "fanSpeed": "HIGH",
        "currentFee": 45.0,
        "fee": 45.0
      }
    ],
    "bill": {
      "roomId": 1,
      "checkinTime": "2025-11-20",
      "checkoutTime": "2025-11-21",
      "duration": "1",
      "roomFee": 100.0,
      "acFee": 45.0
    }
  }
  ```

---

### 2. 空调调度接口 `(/api/ac)`

| 方法 | 路径 | 关键参数 | 说明 |
| --- | --- | --- | --- |
| POST | `/ac/room/{roomId}/start` | Query: `currentTemp`(可选) | 开机并加入调度 |
| POST | `/ac/room/{roomId}/stop` | - | 关机并落地详单 |
| PUT | `/ac/room/{roomId}/temp` | Query: `targetTemp` | 修改目标温度 |
| PUT | `/ac/room/{roomId}/speed` | Query: `fanSpeed`(`LOW/MEDIUM/HIGH`) | 修改风速 |
| GET | `/ac/room/{roomId}/detail` | - | 汇总该房间空调总时长、费用 |
| GET | `/ac/room/{roomId}/status` | - | 返回房间温控状态与排队信息 |
| GET | `/ac/schedule/status` | - | 返回调度队列（服务中/等待中） |

错误示例：若房间未开机调用 stop，将返回 `{"error": "房间空调尚未开启"}`。

---

### 3. 账单接口 `(/api/bills)`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/bills` | 列出所有账单 |
| GET | `/bills/{billId}` | 查询指定账单 |
| GET | `/bills/customer/{customerId}` | 按顾客查询账单 |
| GET | `/bills/room/{roomNumber}` or `/room-id/{roomId}` | 按房间查询 |
| GET | `/bills/unpaid` | 查询未支付账单 |
| POST | `/bills/{billId}/pay` | 账单支付 |
| POST | `/bills/{billId}/cancel` | 取消账单 |
| GET | `/bills/{billId}/details` | 空调详单明细列表 |
| POST | `/bills/{billId}/print` | 生成“空调详单”打印数据，并标记已打印 |
| GET | `/bills/{billId}/export-details` | 导出 CSV（Content-Disposition: attachment） |

**打印接口响应**
```json
{
  "bill": { ... },
  "detailItems": [
    { "startTime": "...", "durationMinutes": 15, "fanSpeed": "HIGH", "cost": 22.5 }
  ],
  "totals": {
    "acDurationMinutes": 45,
    "acFee": 67.5,
    "roomFee": 100.0,
    "grandTotal": 167.5
  }
}
```

---

### 4. 系统管理员维护 `(/api/admin)`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/admin/rooms/{roomId}/offline` | 将房间标记为维修（会强制关机） |
| POST | `/admin/rooms/{roomId}/online` | 维修完成，恢复可用 |
| POST | `/admin/maintenance/force-rotation` | 强制调度轮转，返回最新队列 |
| POST | `/admin/maintenance/simulate-temperature` | 执行一次温度模拟 |

---

### 5. 监控接口 `(/api/monitor)`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/monitor/roomstatus` | 返回每个房间的当前温度、目标温度、风速、开关状态 |
| GET | `/monitor/queuestatus` | 返回服务队列与等待队列的房间列表 |

---

### 6. 运营报表 `(/api/reports)`

| 方法 | 路径 | Query 参数 | 说明 |
| --- | --- | --- | --- |
| GET | `/reports/overview` | `start`, `end`（ISO 字符串，可选） | 返回经营概览：房态统计、收入汇总等 |
| GET | `/reports/ac-usage` | `start`, `end` | 返回空调使用统计（按风速拆分） |
| GET | `/reports/daily-revenue` | `days`（默认 7） | 最近 N 天收入趋势 |

示例返回：
```json
{
  "timeRange": { "start": "2025-11-01", "end": "2025-11-07" },
  "roomStats": { "total": 5, "occupied": 3, "maintenance": 1, "occupancyRate": 0.6 },
  "revenue": { "roomFee": 500, "acFee": 230, "total": 730 },
  "billing": { "billCount": 3, "avgAcFee": 76.67 }
}
```

---

### 7. 测试辅助接口 `(/api/test)`

> 仅用于开发调试环境，谨慎在生产中暴露。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/test/time-slice-check` | 立即执行调度轮转 |
| POST | `/test/temperature-update` | 手动触发一次温度模拟 |
| GET | `/test/rooms/status` | 获取全部房间原始状态 |
| GET | `/test/rooms/{roomId}/status` | 获取单个房间状态 |
| POST | `/test/rooms/{roomId}/temperature?temperature=26` | 手动设置房间当前温度 |
| POST | `/test/reset` | 重置所有房间（清空排队、恢复默认温度） |

---

### 8. 响应示例约定

- 时间统一使用 ISO8601（UTC）字符串，例如 `2025-11-20T10:20:00.000000`
- 金额单位：人民币元；时长单位：分钟
- 风速取值：`LOW` / `MEDIUM` / `HIGH`

如需新增接口，请同步更新本文件，保持字段含义与 README 描述一致。

