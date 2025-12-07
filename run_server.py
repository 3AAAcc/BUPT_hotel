#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务器启动脚本
直接运行: python run_server.py
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
parent_dir = project_root.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from hotel import create_app
from hotel.config import Config

if __name__ == "__main__":
    app = create_app()
    
    # 获取本机IP地址
    import socket
    def get_local_ip():
        try:
            # 连接到一个远程地址来获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    local_ip = get_local_ip()
    
    print(f"=== 服务器启动 ===")
    print(f"本地访问: http://localhost:{Config.SERVER_PORT}")
    print(f"局域网访问: http://{local_ip}:{Config.SERVER_PORT}")
    print(f"其他电脑请使用上述局域网地址访问")
    print("=" * 30)
    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=True)

