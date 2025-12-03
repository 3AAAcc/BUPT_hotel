from flask import Blueprint, jsonify, request
# 注意这里导入的是 ac (ACService) 和 scheduler
from ..services import ac, scheduler

ac_bp = Blueprint("ac", __name__, url_prefix="/ac")

@ac_bp.get("/state")
def request_ac_state():
    room_id = request.args.get("roomId", type=int)
    if not room_id:
        return jsonify({"error": "roomId is required"}), 400
    try:
        # 注意：温度更新由后台任务自动处理，这里不再手动触发
        # 获取状态 (使用我们修复后的 RequestState 方法)
        status = scheduler.RequestState(room_id)
        return jsonify(status)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@ac_bp.post("/power")
def power_on():
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    try:
        # 开机前获取当前温度，避免调度器缺少参数
        from ..services import room_service
        room = room_service.getRoomById(room_id)
        current_temp = room.current_temp if room else None
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
    mode = payload.get("mode")  # Expected: 'COOLING' or 'HEATING'
    try:
        # === 修改：调用 scheduler 的逻辑，而不是直接改数据库 ===
        message = scheduler.ChangeMode(room_id, mode)
        
        # 为了保证前端看到最新状态，强制计算一次
        # 注意：温度更新由后台任务自动处理，这里不再手动触发
        
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400