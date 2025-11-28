from flask import Blueprint, jsonify, request
# 注意这里导入的是 ac (ACService) 和 scheduler
from ..services import ac, scheduler

# === 核心修改：去掉 /api 前缀 ===
ac_bp = Blueprint("ac", __name__, url_prefix="/ac")

@ac_bp.get("/state")
def request_ac_state():
    room_id = request.args.get("roomId", type=int)
    if not room_id:
        return jsonify({"error": "roomId is required"}), 400
    try:
        # 1. 强制触发温度计算 (让温度动起来)
        scheduler.simulateTemperatureUpdate()
        # 2. 获取状态 (使用我们修复后的 RequestState 方法)
        status = scheduler.RequestState(room_id)
        return jsonify(status)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@ac_bp.post("/power")
def power_on():
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    try:
        # 获取房间当前温度（如果提供了则使用，否则为 None，让 PowerOn 使用房间的现有温度）
        from ..services import room_service
        room = room_service.getRoomById(room_id)
        current_temp = room.current_temp if room else None
        # 开机（传递当前温度，如果为 None 则使用房间的现有温度）
        message = ac.PowerOn(room_id, current_temp)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@ac_bp.post("/power/off")
def power_off_endpoint():
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    try:
        # 关机 (调用 scheduler 的 PowerOff 以触发计费周期)
        message = scheduler.PowerOff(room_id)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@ac_bp.post("/temp")
def change_temp():
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    target_temp = payload.get("targetTemp")
    try:
        message = ac.ChangeTemp(room_id, target_temp)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@ac_bp.post("/speed")
def change_speed():
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    fan_speed = payload.get("fanSpeed")
    try:
        message = ac.ChangeSpeed(room_id, fan_speed)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@ac_bp.post("/mode")
def change_mode():
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    mode = payload.get("mode")
    try:
        # 切换模式 (简单实现，直接操作 Room 对象)
        from ..services import room_service
        room = room_service.getRoomById(room_id)
        if room:
            room.ac_mode = mode
            room_service.updateRoom(room)
            return jsonify({"message": "模式已更新"})
        return jsonify({"error": "房间不存在"}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400