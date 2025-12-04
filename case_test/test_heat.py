#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制热工况测试脚本 - 精确流逝版 (修复Dashboard报错)
对应文件: 系统测试用例 热 20251115.xlsx
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# === 配置 ===
API_BASE = "http://127.0.0.1:8080"

# === 核心时间控制参数 ===
SPEED_FACTOR = 6.0  # 6倍速：现实1秒 = 逻辑6秒
LOGICAL_ONE_MINUTE = 60.0  # 逻辑上的1分钟
# 物理上需要等待的时间 = 60 / 6 = 10秒
PHYSICAL_INTERVAL = LOGICAL_ONE_MINUTE / SPEED_FACTOR 

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv", "test_heat.txt")

# 房间配置 (制热)
ROOM_CONFIG = {
    1: {"init_temp": 10.0, "default_temp": 10.0, "rate": 100.0},
    2: {"init_temp": 15.0, "default_temp": 15.0, "rate": 125.0},
    3: {"init_temp": 18.0, "default_temp": 18.0, "rate": 150.0},
    4: {"init_temp": 12.0, "default_temp": 12.0, "rate": 200.0},
    5: {"init_temp": 14.0, "default_temp": 14.0, "rate": 100.0},
}

# 动作序列 (分钟, 房间号, 动作, 参数)
ACTIONS = [
    (1, 1, "power_on", None),
    (2, 1, "temp", 24.0),
    (2, 2, "power_on", None),
    (3, 3, "power_on", None),
    (4, 2, "temp", 25.0),
    (4, 4, "power_on", None),
    (4, 5, "power_on", None),
    (5, 3, "temp", 28.0),
    (5, 5, "speed", "HIGH"),
    (6, 1, "speed", "HIGH"),
    (8, 5, "temp", 24.0),
    (10, 1, "temp", 22.0),
    (10, 4, "temp", 21.0),
    (10, 4, "speed","HIGH"),
    (12, 5, "speed", "MEDIUM"),
    (13, 2, "speed", "HIGH"),
    (15, 1, "power_off", None),
    (15, 3, "speed", "LOW"),
    (17, 5, "power_off", None),
    (18, 3, "speed", "HIGH"),
    (19, 1, "power_on", None),
    (19, 4, "temp", 25.0),
    (19, 4, "speed", "MEDIUM"),
    (21, 2, "temp", 26.0),
    (21, 2, "speed", "MEDIUM"),
    (21, 5, "power_on", None),
    (25, 1, "power_off", None),
    (25, 3, "power_off", None),
    (25, 5, "power_off", None),
    (26, 2, "power_off", None),
    (26, 4, "power_off", None),
]

def log(line: str):
    """打印并记录日志"""
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def init_env():
    """初始化环境：设置倍速、重置房间"""
    log(f">>> 初始化环境 (Speed x{SPEED_FACTOR})...")
    
    # 1. 设置后端时间流速
    try:
        requests.post(f"{API_BASE}/test/time/set_speed", json={"speed": SPEED_FACTOR})
    except Exception as e:
        log(f"[Fatal] 无法设置时间倍速: {e}")
        return

    # 2. 初始化房间状态
    for rid, cfg in ROOM_CONFIG.items():
        try:
            # 强制设为制热模式
            requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": rid, "mode": "HEATING"})
            
            # 初始化状态
            requests.post(f"{API_BASE}/test/initRoom", json={
                "roomId": rid,
                "temperature": cfg["init_temp"],
                "defaultTemp": cfg["default_temp"],
                "dailyRate": cfg["rate"]
            })
        except Exception as e:
            log(f"  × Room {rid} Init Error: {e}")
    
    log(">>> 环境就绪，测试开始\n")

def execute(rid, act, val):
    """执行单个指令"""
    url = f"{API_BASE}/ac"
    try:
        if act == "power_on":
            # 确保模式正确
            requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": rid, "mode": "HEATING"})
            res = requests.post(f"{url}/power", json={"roomId": rid})
        elif act == "power_off":
            res = requests.post(f"{url}/power/off", json={"roomId": rid})
        elif act == "temp":
            res = requests.post(f"{url}/temp", json={"roomId": rid, "targetTemp": val})
        elif act == "speed":
            res = requests.post(f"{url}/speed", json={"roomId": rid, "fanSpeed": val})
        else:
            return f"❌ Unknown: {act}"
        
        status = "✅" if res.status_code == 200 else "⚠️"
        msg = "OK" if res.status_code == 200 else res.json().get('error', 'Fail')
        return f"{status} Room {rid} {act} {val if val else ''} -> {msg}"
    except Exception as e:
        return f"❌ Room {rid} Error: {e}"

def print_dashboard(current_logical_minute):
    """打印仪表盘（包含时间和队列状态）"""
    try:
        # 1. 获取后端时间状态
        t_res = requests.get(f"{API_BASE}/test/time/status").json()
        l_time = t_res.get("logical_time", "")[11:19] # 只取 HH:MM:SS
        
        # 2. 获取房间状态
        r_res = requests.get(f"{API_BASE}/admin/rooms/status").json()
        rooms = sorted(r_res, key=lambda x: x['room_id'])
        
        # 3. 获取队列状态
        q_res = requests.get(f"{API_BASE}/monitor/status").json()
        
        log(f"\n[{l_time}] Logic Min: {current_logical_minute} (Speed x{SPEED_FACTOR})")
        log("-" * 95)
        log(f"{'Rm':<3} {'St':<4} {'Cur':<5} {'Tar':<5} {'Spd':<4} {'RoomFee':<8} {'ACFee':<8} {'Cnt':<4} {'Mode':<8} | {'Queue Status'}")
        log("-" * 95)
        
        # 构建队列信息字典：{roomId: seconds}
        serving_dict = {i['roomId']: int(i.get('servingSeconds', 0)) for i in q_res.get('servingQueue', [])}
        waiting_dict = {i['roomId']: int(i.get('waitingSeconds', 0)) for i in q_res.get('waitingQueue', [])}
        
        serving_ids = list(serving_dict.keys())
        waiting_ids = list(waiting_dict.keys())

        for r in rooms:
            rid = r['room_id']
            st = "ON" if r['ac_on'] else "OFF"
            sp = (r['fan_speed'] or "-")[0]
            mode = (r.get('ac_mode') or r.get('mode') or "-")[:4]
            
            # --- 修复部分：安全获取状态 ---
            q_status = ""
            # 优先使用后端返回的计算好的状态
            backend_state = r.get('state') or r.get('queue_state')
            
            if rid in serving_ids: 
                q_status = f"R{rid}({serving_dict[rid]})"
            elif rid in waiting_ids: 
                q_status = f"W{rid}({waiting_dict[rid]})"
            # 使用 .get() 安全访问，或者检查后端返回的 state 字段
            elif r.get('cooling_paused') or backend_state == "PAUSED": 
                q_status = "PAUSED"
            elif st == "OFF":
                q_status = "OFF"
            else:
                q_status = "IDLE"
            
            room_fee = r.get('room_fee', 0.0)
            ac_fee = r.get('ac_fee', 0.0)
            schedule_count = r.get('schedule_count', 0)
            log(f"{rid:<3} {st:<4} {r['current_temp']:<5.1f} {r['target_temp']:<5} {sp:<4} {room_fee:<8.2f} {ac_fee:<8.2f} {schedule_count:<4} {mode:<8} | {q_status}")
            
        log("-" * 75)

    except Exception as e:
        log(f"[Dashboard Error] {e}")

def main():
    # 0. 准备日志
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"=== Heat Test Started at {time.strftime('%H:%M:%S')} ===\n")
    except: pass

    init_env()
    
    # 1. 构建动作映射
    actions_map = {}
    for t, r, a, v in ACTIONS:
        if t not in actions_map: actions_map[t] = []
        actions_map[t].append((r, a, v))
    
    max_minute = 30
    
    # === 关键逻辑：锚点时间同步 ===
    start_time_physical = time.time()
    
    for minute in range(max_minute + 1):
        # --- A. 执行本分钟动作 ---
        if minute in actions_map:
            log(f"⚡ Action Trigger (Min {minute})")
            with ThreadPoolExecutor() as ex:
                futures = [ex.submit(execute, r, a, v) for r, a, v in actions_map[minute]]
                for f in as_completed(futures):
                    log(f"  {f.result()}")
        
        # --- B. 打印状态快照 ---
        time.sleep(0.2) 
        print_dashboard(minute)
        
        # --- C. 精确等待下一分钟 ---
        if minute < max_minute:
            target_physical_time = start_time_physical + ((minute + 1) * PHYSICAL_INTERVAL)
            current_physical_time = time.time()
            sleep_duration = target_physical_time - current_physical_time
            
            if sleep_duration > 0:
                print(f"   ... flowing ({sleep_duration:.2f}s) ...", end="\r")
                time.sleep(sleep_duration)
            else:
                log(f"⚠️ System Lagging! Behind by {abs(sleep_duration):.2f}s")

    log("\n=== Test Completed ===")

if __name__ == "__main__":
    main()