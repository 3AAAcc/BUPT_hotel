#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制冷工况测试脚本 (test_case_cool.py) - 修复版
对应文件: 系统测试用例 冷 20251115.xlsx
修复内容：
1. 强制同步后端时间倍速 (x6.0)
2. 使用物理时间锚点消除 sleep 误差
3. 确保日志清晰
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# === 配置 ===
API_BASE = "http://127.0.0.1:8000"

# === 核心时间控制参数 (与 test_heat.py 保持一致) ===
SPEED_FACTOR = 6.0  # 6倍速：现实1秒 = 逻辑6秒
LOGICAL_ONE_MINUTE = 60  # 逻辑上的1分钟
# 物理上需要等待的时间 = 60 / 6 = 10秒
PHYSICAL_INTERVAL = LOGICAL_ONE_MINUTE / SPEED_FACTOR 

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv", "test_cool.txt")

# 房间配置 (制冷)
ROOM_CONFIG = {
    1: {"init_temp": 32.0, "default_temp": 32.0, "rate": 100.0},
    2: {"init_temp": 28.0, "default_temp": 28.0, "rate": 125.0},
    3: {"init_temp": 30.0, "default_temp": 30.0, "rate": 150.0},
    4: {"init_temp": 29.0, "default_temp": 29.0, "rate": 200.0},
    5: {"init_temp": 35.0, "default_temp": 35.0, "rate": 100.0},
}

# 动作序列 (分钟, 房间, 动作, 值)
ACTIONS = [
    (0, 1, "power_on", None),
    (1, 1, "temp", 18.0),
    (1, 2, "power_on", None),
    (1, 5, "power_on", None),
    (2, 3, "power_on", None),
    (3, 2, "temp", 19.0),
    (3, 4, "power_on", None),
    (4, 5, "temp", 22.0),
    (5, 1, "speed", "HIGH"),
    (6, 2, "power_off", None),
    (7, 2, "power_on", None),
    (7, 5, "speed", "HIGH"),
    (9, 1, "temp", 22.0),
    (9, 4, "temp", 18.0),
    (9, 4, "speed", "HIGH"),
    (11, 2, "temp", 22.0),
    (12, 5, "speed", "LOW"),
    (14, 1, "power_off", None),
    (14, 3, "temp", 24.0),
    (14, 3, "speed", "LOW"),
    (15, 5, "temp", 20.0),
    (15, 5, "speed", "HIGH"),
    (16, 2, "power_off", None),
    (17, 3, "speed", "HIGH"),
    (18, 1, "power_on", None),
    (18, 4, "temp", 20.0),
    (18, 4, "speed", "MEDIUM"),
    (19, 2, "power_on", None),
    (20, 5, "temp", 25.0),
    (22, 3, "power_off", None),
    (23, 5, "power_off", None),
    (24, 1, "power_off", None),
    (25, 4, "power_off", None),
    (25, 2, "power_off", None),
]

def log(line: str):
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def init_env():
    log(f">>> 初始化环境 (Speed x{SPEED_FACTOR})...")
    
    # 1. 设置后端时间流速 (关键!)
    try:
        requests.post(f"{API_BASE}/test/time/set_speed", json={"speed": SPEED_FACTOR})
    except Exception as e:
        log(f"[Fatal] 无法设置时间倍速: {e}")
        return

    # 2. 初始化房间
    for rid, cfg in ROOM_CONFIG.items():
        try:
            # 强制制冷模式
            requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": rid, "mode": "COOLING"})

            requests.post(f"{API_BASE}/test/initRoom", json={
                "roomId": rid,
                "temperature": cfg["init_temp"],
                "defaultTemp": cfg["default_temp"],
                "dailyRate": cfg["rate"]
            })
            print(f"  √ Room {rid}: Temp={cfg['init_temp']}°C, Rate={cfg['rate']}")
        except Exception as e:
            print(f"  × Room {rid} Error: {e}")

    # 3. 为每个房间办理入住
    checkin_config = {
        1: {"name": "109c", "idCard": "123456", "phoneNumber": "123456"},
        2: {"name": "109d", "idCard": "123456", "phoneNumber": "123456"},
        3: {"name": "110e", "idCard": "123456", "phoneNumber": "123456"},
        4: {"name": "room4", "idCard": "123456", "phoneNumber": "123456"},
        5: {"name": "room5", "idCard": "123456", "phoneNumber": "123456"},
    }

    print("\n>>> 开始办理入住...")
    for rid, customer_info in checkin_config.items():
        try:
            response = requests.post(f"{API_BASE}/hotel/checkin", json={
                "roomId": rid,
                "name": customer_info["name"],
                "idCard": customer_info["idCard"],
                "phoneNumber": customer_info["phoneNumber"]
            })
            if response.status_code == 200:
                print(f"  √ Room {rid} 入住成功: {customer_info['name']}")
            else:
                print(f"  × Room {rid} 入住失败: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            print(f"  × Room {rid} 入住错误: {e}")

    print(">>> 初始化完成\n")

def execute(rid, act, val):
    url = f"{API_BASE}/ac"
    try:
        if act == "power_on":
            # 确保模式正确
            requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": rid, "mode": "COOLING"})
            res = requests.post(f"{url}/power", json={"roomId": rid})
        elif act == "power_off":
            res = requests.post(f"{url}/power/off", json={"roomId": rid})
        elif act == "temp":
            res = requests.post(f"{url}/temp", json={"roomId": rid, "targetTemp": val})
        elif act == "speed":
            res = requests.post(f"{url}/speed", json={"roomId": rid, "fanSpeed": val})
        
        msg = "OK" if res.status_code == 200 else res.json().get('error', 'Fail')
        return f"Room {rid} {act} {val if val else ''} -> {msg}"
    except Exception as e:
        return f"Room {rid} Error: {e}"

def print_dashboard(current_logical_minute):
    try:
        # 1. 获取后端时间
        t_res = requests.get(f"{API_BASE}/test/time/status").json()
        l_time = t_res.get("logical_time", "")[11:19]
        
        # 2. 获取房间状态
        r_res = requests.get(f"{API_BASE}/admin/rooms/status").json()
        rooms = sorted(r_res, key=lambda x: x['room_id'])
        
        # 3. 获取队列状态
        q_res = requests.get(f"{API_BASE}/monitor/status").json()
        
        log(f"\n[{l_time}] Logic Min: {current_logical_minute} (Speed x{SPEED_FACTOR})")
        log("-" * 95)
        log(f"{'Rm':<3} {'St':<4} {'Cur':<5} {'Tar':<5} {'Spd':<4} {'RoomFee':<8} {'ACFee':<8} {'Total':<8} {'Cnt':<4} {'Mode':<8} | {'Queue Status'}")
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
            
            q_status = ""
            if rid in serving_ids: 
                q_status = f"R{rid}({serving_dict[rid]})"
            elif rid in waiting_ids: 
                q_status = f"W{rid}({waiting_dict[rid]})"
            elif r.get('cooling_paused'): 
                q_status = "PAUSED"
            elif st == "OFF": 
                q_status = "OFF"
            else: 
                q_status = "IDLE"
            
            room_fee = r.get('room_fee', 0.0)
            ac_fee = r.get('ac_fee', 0.0)
            total_cost = r.get('total_cost', 0.0)
            schedule_count = r.get('schedule_count', 0)
            log(f"{rid:<3} {st:<4} {r['current_temp']:<5.1f} {r['target_temp']:<5} {sp:<4} {room_fee:<8.2f} {ac_fee:<8.2f} {total_cost:<8.2f} {schedule_count:<4} {mode:<8} | {q_status}")
        log("-" * 83)
    except Exception as e:
        log(f"[Dashboard Error] {e}")

def main():
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"=== Cool Test Started at {time.strftime('%H:%M:%S')} ===\n")
    except: pass

    init_env()
    
    actions_map = {}
    for t, r, a, v in ACTIONS:
        if t not in actions_map: actions_map[t] = []
        actions_map[t].append((r, a, v))
    
    max_minute = 30
    
    # === 关键: 物理锚点同步 ===
    start_time_physical = time.time()
    
    for minute in range(max_minute + 1):
        # A. 执行动作
        if minute in actions_map:
            log(f"⚡ Action Trigger (Min {minute})")
            with ThreadPoolExecutor() as ex:
                futures = [ex.submit(execute, r, a, v) for r, a, v in actions_map[minute]]
                for f in as_completed(futures):
                    log(f"  {f.result()}")
        
        # B. 打印
        time.sleep(0.2)
        print_dashboard(minute)
        
        # C. 精确等待
        if minute < max_minute:
            target = start_time_physical + ((minute + 1) * PHYSICAL_INTERVAL)
            curr = time.time()
            sleep_sec = target - curr
            if sleep_sec > 0:
                print(f"   ... flowing ({sleep_sec:.2f}s) ...", end="\r")
                time.sleep(sleep_sec)
            else:
                log(f"⚠️ Lagging {abs(sleep_sec):.2f}s")

    log("\n=== Test Completed ===")

if __name__ == "__main__":
    main()