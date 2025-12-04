#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Room 1 等待队列回温问题复现脚本
用于调试 Room 1 在等待队列中错误升温的问题
"""

import time
import requests
import os

# === 配置 ===
API_BASE = "http://127.0.0.1:8080"
TIME_FACTOR = 60
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv", "test_room1_waiting.txt")


def log(line: str):
    """同时打印到控制台并追加写入日志文件"""
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def init_room(room_id: int, init_temp: float, default_temp: float, rate: float):
    """初始化房间"""
    try:
        # 1. 设置模式为制热
        mode_res = requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": room_id, "mode": "HEATING"})
        if mode_res.status_code != 200:
            log(f"  ⚠️ Room {room_id} 模式设置失败: {mode_res.text}")
            return False

        # 2. 初始化温度和默认温度
        init_res = requests.post(f"{API_BASE}/test/initRoom", json={
            "roomId": room_id,
            "temperature": init_temp,
            "defaultTemp": default_temp,  # === 关键：单独设置 default_temp ===
            "dailyRate": rate
        })
        if init_res.status_code != 200:
            log(f"  ⚠️ Room {room_id} 初始化失败: {init_res.text}")
            return False

        # 3. 确保 default_temp 被正确设置（通过更新房间）
        # 注意：test_controller 已经设置了 default_temp，但为了确保，我们再次确认
        room_res = requests.get(f"{API_BASE}/admin/rooms/status")
        if room_res.status_code == 200:
            rooms = room_res.json()
            for r in rooms:
                if r['room_id'] == room_id:
                    log(f"  √ Room {room_id}: Mode=HEATING, Temp={r['current_temp']}°C, "
                        f"DefaultTemp={r.get('default_temp', 'N/A')}°C, Rate={rate}")
                    break

        return True
    except Exception as e:
        log(f"  × Room {room_id} Error: {e}")
        return False


def execute(room_id: int, action: str, value=None):
    """执行操作"""
    url = f"{API_BASE}/ac"
    try:
        if action == "power_on":
            mode_res = requests.post(f"{API_BASE}/admin/control/mode", json={"roomId": room_id, "mode": "HEATING"})
            if mode_res.status_code != 200:
                return f"⚠️ Room {room_id} 模式设置失败"
            res = requests.post(f"{url}/power", json={"roomId": room_id})
        elif action == "power_off":
            res = requests.post(f"{url}/power/off", json={"roomId": room_id})
        elif action == "temp":
            res = requests.post(f"{url}/temp", json={"roomId": room_id, "targetTemp": value})
        elif action == "speed":
            res = requests.post(f"{url}/speed", json={"roomId": room_id, "fanSpeed": value})
        else:
            return f"❌ Room {room_id} 未知动作: {action}"

        status = "✅" if res.status_code == 200 else "⚠️"
        msg = "成功" if res.status_code == 200 else f"失败: {res.json().get('error', '未知')}"
        return f"{status} Room {room_id} {action} {value if value else ''} -> {msg}"
    except Exception as e:
        return f"❌ Room {room_id} Error: {e}"


def print_status():
    """打印房间状态"""
    try:
        res = requests.get(f"{API_BASE}/admin/rooms/status")
        data = sorted(res.json(), key=lambda x: x['room_id'])
        log("-" * 65)
        log(f"{'Rm':<3} {'St':<4} {'Cur':<6} {'Tar':<5} {'Spd':<4} {'Fee':<8} {'Mode':<8} {'Default'}")
        log("-" * 65)
        for r in data:
            st = "ON" if r['ac_on'] else "OFF"
            sp = (r['fan_speed'] or "-")[0]
            default_temp = r.get('default_temp', 'N/A')
            if isinstance(default_temp, (int, float)):
                default_temp = f"{default_temp:.1f}"
            log(
                f"{r['room_id']:<3} {st:<4} {r['current_temp']:<6.2f} {r['target_temp']:<5.1f} {sp:<4} "
                f"{r['total_cost']:<8.2f} {r['ac_mode']:<8} {default_temp}")
        log("-" * 65 + "\n")
    except Exception as e:
        log(f"获取状态失败: {e}")


def print_queue():
    """打印队列状态"""
    try:
        res = requests.get(f"{API_BASE}/monitor/status")
        data = res.json()
        log("=== Queue Status ===")
        log(f"Capacity={data.get('capacity')}  TimeSlice={data.get('timeSlice')}s")

        log("ServingQueue:")
        for item in data.get("servingQueue", []):
            log(f"  Room {item['roomId']}  "
                f"Fan={item['fanSpeed']}  "
                f"Slice={item['servingSeconds']:.1f}s  "
                f"Total={item.get('totalSeconds', item['servingSeconds']):.0f}s")

        log("WaitingQueue:")
        for item in data.get("waitingQueue", []):
            log(f"  Room {item['roomId']}  "
                f"Fan={item['fanSpeed']}  "
                f"Wait={item['waitingSeconds']:.1f}s")
        log("====================\n")
    except Exception as e:
        log(f"获取队列状态失败: {e}")


def get_room1_details():
    """获取 Room 1 的详细信息"""
    try:
        res = requests.get(f"{API_BASE}/admin/rooms/status")
        if res.status_code == 200:
            rooms = res.json()
            for r in rooms:
                if r['room_id'] == 1:
                    return r
        return None
    except:
        return None


def main():
    # 清空日志
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("=== test_room1_waiting start ===\n")
    except:
        pass

    log("=" * 70)
    log("Room 1 等待队列回温问题复现脚本")
    log("=" * 70)
    log("")

    # 1. 初始化 Room 1: 温度 12.0，默认温度 10.0
    log(">>> 步骤 1: 初始化 Room 1")
    log("   Room 1: init_temp=12.0°C, default_temp=10.0°C (应该向 10.0°C 回温)")
    if not init_room(1, 12.0, 10.0, 100.0):
        log("初始化失败，退出")
        return
    log("")

    # 2. 初始化其他房间，用于占满服务队列
    log(">>> 步骤 2: 初始化其他房间（用于占满服务队列）")
    init_room(2, 15.0, 15.0, 125.0)
    init_room(3, 18.0, 18.0, 150.0)
    init_room(4, 12.0, 12.0, 200.0)
    init_room(5, 14.0, 14.0, 100.0)
    log("")

    # 3. 先开启其他房间，占满服务队列（容量通常是3）
    log(">>> 步骤 3: 开启其他房间，占满服务队列")
    log("  [Min 0]")
    execute(2, "power_on")
    execute(2, "temp", 25.0)
    time.sleep(0.5)
    execute(4, "power_on")
    execute(4, "temp", 22.0)
    time.sleep(0.5)
    execute(5, "power_on")
    execute(5, "temp", 22.0)
    execute(5, "speed", "HIGH")
    time.sleep(0.5)
    print_status()
    print_queue()
    log("")

    # 4. 开启 Room 1，目标温度 24.0，应该进入等待队列
    log(">>> 步骤 4: 开启 Room 1，目标温度 24.0（应该进入等待队列）")
    log("  [Min 1]")
    execute(1, "power_on")
    execute(1, "temp", 24.0)
    time.sleep(0.5)
    print_status()
    print_queue()
    
    # 确认 Room 1 在等待队列中
    room1 = get_room1_details()
    if room1:
        log(f"Room 1 状态: ac_on={room1['ac_on']}, current_temp={room1['current_temp']:.2f}, "
            f"target_temp={room1['target_temp']:.1f}, default_temp={room1.get('default_temp', 'N/A')}")
    log("")

    # 5. 观察 Room 1 的温度变化（应该向 10.0°C 回温，而不是升温）
    log(">>> 步骤 5: 观察 Room 1 的温度变化（应该向 10.0°C 回温）")
    log("  等待 1 分钟，观察温度变化...")
    log("")
    
    initial_temp = room1['current_temp'] if room1 else None
    log(f"  [Min 2] 初始温度: {initial_temp:.2f}°C")
    print_status()
    print_queue()
    
    # 等待 1 分钟
    time.sleep(TIME_FACTOR)
    
    room1_after = get_room1_details()
    if room1_after and initial_temp:
        temp_change = room1_after['current_temp'] - initial_temp
        expected_change = -0.5  # 应该降温 0.5 度/分钟
        log(f"  [Min 3] 1分钟后温度: {room1_after['current_temp']:.2f}°C")
        log(f"  温度变化: {temp_change:+.2f}°C (期望: {expected_change:.2f}°C)")
        if temp_change > 0:
            log(f"  ❌ 错误：Room 1 在等待队列中却升温了！应该向 10.0°C 回温（降温）")
        elif abs(temp_change - expected_change) > 0.1:
            log(f"  ⚠️ 警告：温度变化不符合预期（期望 {expected_change:.2f}°C，实际 {temp_change:+.2f}°C）")
        else:
            log(f"  ✅ 正确：温度变化符合预期")
    print_status()
    print_queue()
    log("")

    # 6. 再等待 1 分钟，继续观察
    log(">>> 步骤 6: 继续观察 1 分钟")
    if room1_after:
        temp_before = room1_after['current_temp']
        log(f"  [Min 4] 当前温度: {temp_before:.2f}°C")
        time.sleep(TIME_FACTOR)
        
        room1_final = get_room1_details()
        if room1_final:
            temp_change2 = room1_final['current_temp'] - temp_before
            log(f"  [Min 5] 1分钟后温度: {room1_final['current_temp']:.2f}°C")
            log(f"  温度变化: {temp_change2:+.2f}°C (期望: -0.5°C)")
            if temp_change2 > 0:
                log(f"  ❌ 错误：Room 1 在等待队列中却升温了！")
    print_status()
    print_queue()
    log("")

    log("=" * 70)
    log("测试完成")
    log("=" * 70)


if __name__ == "__main__":
    main()

