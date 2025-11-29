#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制热工况测试脚本 (test_case_heat.py)
对应文件: 系统测试用例 热 20251115.xlsx
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# === 配置 ===
API_BASE = "http://127.0.0.1:8080"
TIME_FACTOR = 10
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv", "test_heat.txt")


def log(line: str):
    """同时打印到控制台并追加写入日志文件"""
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # 写文件失败时不影响测试继续运行
        pass

# 房间配置 (制热 - 初始温度低)
ROOM_CONFIG = {
    1: {"init_temp": 10.0, "rate": 100.0},
    2: {"init_temp": 15.0, "rate": 125.0},
    3: {"init_temp": 18.0, "rate": 150.0},
    4: {"init_temp": 12.0, "rate": 200.0},
    5: {"init_temp": 14.0, "rate": 100.0},
}

# 动作序列 (制热)
ACTIONS = [
    (1, 1, "power_on", None),
    (2, 1, "temp", 24.0),
    (2, 2, "power_on", None),
    (3, 3, "power_on", None),
    (4, 2, "temp", 25.0),
    (4, 4, "power_on", None),
    (4, 5, "power_on", None),
    (5, 3, "temp", 27.0),  # 注：可能超出范围(18-25)
    (5, 5, "speed", "HIGH"),
    (6, 1, "speed", "HIGH"),
    (8, 5, "temp", 24.0),
    (10, 1, "temp", 28.0),  # 注：可能超出范围
    (10, 4, "temp", 28.0),  # 注：可能超出范围
    (10, 4, "speed", "HIGH"),
    (12, 5, "speed", "MEDIUM"),
    (13, 2, "speed", "HIGH"),
    (15, 1, "power_off", None),
    (15, 3, "speed", "LOW"),
    (17, 5, "power_off", None),
    (18, 3, "speed", "HIGH"),
    (19, 1, "power_on", None),
    (19, 4, "temp", 25.0),
    (19, 4, "speed", "MEDIUM"),
    (21, 2, "temp", 27.0),  # 注：可能超出范围
    (21, 2, "speed", "MEDIUM"),
    (21, 5, "power_on", None),
    (25, 1, "power_off", None),
    (25, 3, "power_off", None),
    (25, 5, "power_off", None),
    (26, 2, "power_off", None),
    (26, 4, "power_off", None),
]


def init_env():
    print(">>> 初始化环境...")
    for rid, cfg in ROOM_CONFIG.items():
        try:
            # 1. 强制切换模式 (保持不变)
            requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": rid, "mode": "HEATING"})  # 或 HEATING

            # 2. 初始化温度 AND 房费 (修改这里!)
            requests.post(f"{API_BASE}/test/initRoom", json={
                "roomId": rid,
                "temperature": cfg["init_temp"],
                "dailyRate": cfg["rate"]  # <--- 新增这行，把配置里的价格传过去
            })

            print(f"  √ Room {rid}: Temp={cfg['init_temp']}°C, Rate={cfg['rate']}")
        except Exception as e:
            print(f"  × Room {rid} Error: {e}")
    print(">>> 初始化完成\n")


def execute(rid, act, val):
    url = f"{API_BASE}/ac"
    try:
        if act == "power_on":
            res = requests.post(f"{url}/power", json={"roomId": rid})
        elif act == "power_off":
            res = requests.post(f"{url}/power/off", json={"roomId": rid})
        elif act == "temp":
            res = requests.post(f"{url}/temp", json={"roomId": rid, "targetTemp": val})
        elif act == "speed":
            res = requests.post(f"{url}/speed", json={"roomId": rid, "fanSpeed": val})

        status = "✅" if res.status_code == 200 else "⚠️"
        msg = "成功" if res.status_code == 200 else f"失败: {res.json().get('error', '未知')}"
        return f"{status} Room {rid} {act} {val if val else ''} -> {msg}"
    except Exception as e:
        return f"❌ Room {rid} Error: {e}"


def print_status():
    try:
        res = requests.get(f"{API_BASE}/admin/rooms/status")
        data = sorted(res.json(), key=lambda x: x['room_id'])
        log("-" * 65)
        log(f"{'Rm':<3} {'St':<4} {'Cur':<5} {'Tar':<5} {'Spd':<4} {'Fee':<8} {'Mode'}")
        log("-" * 65)
        for r in data:
            st = "ON" if r['ac_on'] else "OFF"
            sp = (r['fan_speed'] or "-")[0]
            log(
                f"{r['room_id']:<3} {st:<4} {r['current_temp']:<5} {r['target_temp']:<5} {sp:<4} {r['total_cost']:<8.2f} {r['ac_mode']}")
        log("-" * 65 + "\n")
    except:
        pass


def print_queue():
    """打印当前调度队列（服务队列 + 等待队列）"""
    try:
        res = requests.get(f"{API_BASE}/monitor/status")
        data = res.json()
        log("=== Queue Status ===")
        log(f"Capacity={data.get('capacity')}  TimeSlice={data.get('timeSlice')}s")

        log("ServingQueue:")
        for item in data.get("servingQueue", []):
            log(f"  Room {item['roomId']}  "
                f"Fan={item['fanSpeed']}  "
                f"Serve={item['servingSeconds']:.1f}s  "
                f"Wait={item['waitingSeconds']:.1f}s")

        log("WaitingQueue:")
        for item in data.get("waitingQueue", []):
            log(f"  Room {item['roomId']}  "
                f"Fan={item['fanSpeed']}  "
                f"Serve={item['servingSeconds']:.1f}s  "
                f"Wait={item['waitingSeconds']:.1f}s")
        log("====================\n")
    except Exception as e:
        print(f"[WARN] 获取队列状态失败: {e}")


def main():
    # 启动前清空旧日志
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("=== test_heat start ===\n")
    except Exception:
        pass

    init_env()
    actions_map = {}
    for t, r, a, v in ACTIONS:
        if t not in actions_map: actions_map[t] = []
        actions_map[t].append((r, a, v))

    max_t = max(actions_map.keys())
    for t in range(max_t + 2):
        log(f"🔥 [Min {t}]")
        if t in actions_map:
            with ThreadPoolExecutor() as ex:
                futures = [ex.submit(execute, r, a, v) for r, a, v in actions_map[t]]
                for f in as_completed(futures):
                    log(f"  {f.result()}")

        time.sleep(0.5)
        print_status()
        print_queue()
        if t < max_t + 1:
            time.sleep(TIME_FACTOR)


if __name__ == "__main__":
    main()