#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制冷工况测试脚本 (test_case_cool.py)
对应文件: 系统测试用例 冷 20251115.xlsx
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# === 配置 ===
API_BASE = "http://127.0.0.1:8080"  # 请确认你的端口
TIME_FACTOR = 10  # 1分钟 = 10秒
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv", "test_cool.txt")


def log(line: str):
    """同时打印到控制台并追加写入日志文件"""
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # 写文件失败时不影响测试继续运行
        pass

# 房间配置 (制冷)
ROOM_CONFIG = {
    1: {"init_temp": 32.0, "rate": 100.0},
    2: {"init_temp": 28.0, "rate": 125.0},
    3: {"init_temp": 30.0, "rate": 150.0},
    4: {"init_temp": 29.0, "rate": 200.0},
    5: {"init_temp": 35.0, "rate": 100.0},
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


def init_env():
    print(">>> 初始化环境...")
    for rid, cfg in ROOM_CONFIG.items():
        try:
            # 1. 强制切换模式 (保持不变)
            requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": rid, "mode": "COOLING"})  # 或 HEATING

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

        # 允许部分操作失败(如超出温度范围)，仅打印结果
        msg = "成功" if res.status_code == 200 else f"失败({res.text})"
        return f"Room {rid} {act} {val if val else ''} -> {msg}"
    except Exception as e:
        return f"Room {rid} Error: {e}"


def print_status():
    try:
        res = requests.get(f"{API_BASE}/admin/rooms/status")
        data = sorted(res.json(), key=lambda x: x['room_id'])
        log("-" * 60)
        log(f"{'Rm':<3} {'St':<4} {'Cur':<5} {'Tar':<5} {'Spd':<4} {'Fee':<8} {'Mode'}")
        log("-" * 60)
        for r in data:
            st = "ON" if r['ac_on'] else "OFF"
            sp = (r['fan_speed'] or "-")[0]  # 取首字母
            log(
                f"{r['room_id']:<3} {st:<4} {r['current_temp']:<5} {r['target_temp']:<5} {sp:<4} {r['total_cost']:<8.2f} {r['ac_mode']}")
        log("-" * 60 + "\n")
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
            f.write("=== test_cool start ===\n")
    except Exception:
        pass

    init_env()
    actions_map = {}
    for t, r, a, v in ACTIONS:
        if t not in actions_map: actions_map[t] = []
        actions_map[t].append((r, a, v))

    max_t = max(actions_map.keys())
    for t in range(max_t + 2):
        log(f"🕒 [Min {t}]")
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