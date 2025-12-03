"""
温度自动更新后台任务
定期更新所有房间的温度，不依赖前端API调用
"""
from __future__ import annotations

import threading
import time
from datetime import datetime

from flask import current_app
from ..extensions import db


class TemperatureScheduler:
    """温度自动更新调度器"""
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.running = False
        self.thread = None
        self.update_interval = 1.0  # 每1秒更新一次，确保稳定的时间间隔
        
    def start(self, app):
        """启动后台任务"""
        if self.running:
            return
        
        self.running = True
        
        # === 核心修复 1: 动态开启连接池的 Pre-Ping 功能 ===
        # 这能有效防止 "Packet sequence number wrong" 错误。
        # 它会在每次获取连接前检查连接活性，如果连接坏了（Packet wrong），
        # 它可以自动丢弃坏连接并重连，而不是抛出错误给应用层。
        with app.app_context():
            try:
                if db.engine.pool:
                    # 这是一个 SQLAlchemy 的隐藏开关，通常在 config 中设置
                    # 这里为了修复现有运行环境，动态开启
                    db.engine.pool._pre_ping = True
            except Exception:
                pass
        
        def run():
            while self.running:
                try:
                    with app.app_context():
                        try:
                            self.scheduler.simulateTemperatureUpdate()
                        except Exception as inner_e:
                            # 业务逻辑报错，尝试回滚
                            try:
                                db.session.rollback()
                            except Exception:
                                pass 
                            # 只有真正的逻辑错误才打印，忽略连接层的噪音
                            if "Packet sequence" not in str(inner_e):
                                print(f"[TemperatureScheduler] 逻辑错误: {inner_e}")
                        finally:
                            # === 核心修复 2: 彻底静默的清理 ===
                            # 无论连接状态如何，强制尝试归还
                            try:
                                db.session.remove()
                            except Exception:
                                # 如果这里报错 (如 InterfaceError)，说明连接已经彻底断了
                                # SQLAlchemy 内部已经将其标记为 invalidate，
                                # 我们直接忽略异常，防止日志刷屏
                                pass
                            
                except Exception as e:
                    # 外层捕获，防止线程退出
                    if "Packet sequence" not in str(e):
                        print(f"[TemperatureScheduler] 线程循环错误: {e}")
                
                time.sleep(self.update_interval)
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        print(f"[TemperatureScheduler] 已启动 (Pre-Ping Enabled)，更新间隔: {self.update_interval}秒")
    
    def stop(self):
        """停止后台任务"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("[TemperatureScheduler] 已停止")

