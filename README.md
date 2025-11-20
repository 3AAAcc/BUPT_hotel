## Python 版酒店空调管理系统

该目录提供了基于 **Python + Flask** 的后端实现，保持与原 Java 版本一致的接口与函数命名，并使用 **HTML + Jinja2** 作为前端模板层、**MySQL** 作为持久化数据库。

### 快速启动

1. 安装依赖：
   ```bash
   pip install -r hotel/requirements.txt
   ```
2. 初始化数据库（会自动创建表并写入基础配置/房间数据）：
   ```bash
   python -m hotel.database.init_db
   ```
   > 如需自定义连接，设置 `DATABASE_URL=mysql+pymysql://user:pwd@host:3306/db?charset=utf8mb4`

3. 运行服务：
   ```bash
   python -m hotel.app
   ```

服务启动后：
- REST API 仍为 `/api/*` 前缀，路由、函数名与 README 中保持一致。
- 浏览器访问 `http://localhost:8080/` 可查看 Jinja2 渲染的监控面板。

