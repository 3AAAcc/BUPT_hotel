## Python 版酒店空调管理系统

该项目提供波普特酒店中央温控系统的 Python 实现，核心目标是：

- 提供“多用多付”空调计费能力，可查询详单、打印账单
- 管理入住/退房流程，自动结算住宿费与空调费
- 让系统管理员维护空调调度队列、模拟温度
- 为酒店经理输出运营报表，支撑 UC01-UC06 用例

技术栈：**Flask + SQLAlchemy + MySQL + Jinja2**，REST API 保持与原 Java 版本兼容。

---

### 功能概览

- **入住/退房**：`/api/hotel/*`
- **空调调度**：`/api/ac/*`，含启停、调温、调速、状态查询
- **账单管理**：`/api/bills/*`，含打印、导出详单
- **监控面板**：`/api/monitor/*` 提供房态与调度队列，前端位于 `templates/dashboard.html`
- **系统维护**：`/api/admin/*` 支持房间维修/恢复、强制轮转、温度模拟
- **运营报表**：`/api/reports/*` 输出经营概览、空调使用统计与营收趋势

详细接口参数请参考 `docs/api_reference.md`。

---

### 目录结构

```
hotel/
├─ app.py                # Flask 入口
├─ config.py             # 配置常量/环境变量
├─ controllers/          # 各类 REST 控制器
├─ services/             # 业务服务与调度逻辑
├─ models/               # SQLAlchemy ORM 模型
├─ database/             # schema.sql、初始化脚本
├─ templates/dashboard.html
├─ static/styles.css
└─ docs/api_reference.md # 接口说明（新增）
```

---

### 环境配置

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `mysql+pymysql://root:abc123456@localhost:3306/hotel_ac_db?charset=utf8mb4` | MySQL 连接串 |
| `HOTEL_AC_TOTAL_COUNT` | `3` | 可同时服务的空调实例数 |
| `HOTEL_ROOM_COUNT` | `5` | 自动初始化的房间数量 |
| `HOTEL_DEFAULT_TEMP` | `25` | 入住默认室温 |
| `HOTEL_TIME_SLICE` | `120` | 调度轮转时间片（秒） |
| `BILLING_ROOM_RATE` | `100` | 住宿费（元/天） |
| `BILLING_AC_RATE_LOW/MEDIUM/HIGH` | `0.5 / 1.0 / 1.5` | 按风速计费（元/分钟） |

---

### 快速启动

1. 安装依赖
   ```bash
   pip install -r hotel/requirements.txt
   ```
2. 初始化数据库（自动执行 `schema.sql` 并写入基础配置、房间数据）
   ```bash
   python -m hotel.database.init_db
   ```
3. 运行服务
   ```bash
   python -m hotel.app
   ```

服务启动后：

- API 前缀统一为 `/api/*`
- 访问 `http://localhost:8080/` 可查看监控面板

---

### 新增能力补充

- `/api/bills/<billId>/print`：生成“空调详单”打印数据，自动标记账单已打印
- `/api/bills/<billId>/export-details`：导出指定账单的空调详单 CSV
- `/api/admin/*`：系统管理员可切换房间维修/可用状态，并触发调度轮转或温度模拟
- `/api/reports/*`：酒店经理查看运营概览、空调使用统计与每日营收趋势

---

### 开发与调试

- `python -m hotel.database.init_db` 可重复执行以清空并重建数据库
- `controllers/test_controller.py` 暴露若干测试路由，例如 `/api/test/reset` 用于重置房间状态
- 建议使用 `flask shell` 或 `python -m hotel.app` 的 `debug=True` 模式进行本地调试

---

### 后续方向

- 完善自动化测试（当前暂无）
- 对接真实前端/物联网设备，替换模拟温度逻辑
- 接入身份认证与角色权限控制，限制维护/报表接口的访问

